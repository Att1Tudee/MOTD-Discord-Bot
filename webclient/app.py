# app.py
from quart import Quart, make_response, render_template, request, jsonify, url_for, redirect
from dbhelper import Dbhelper
from bson import ObjectId

app = Quart(__name__)
db_helper = Dbhelper()

@app.route('/')
async def index():
    collection_names = await db_helper.db.list_collection_names()
    all_docs = {}
    for collection_name in collection_names:
        documents = await db_helper.db[collection_name].find().to_list(length=100)
        all_docs[collection_name] = documents
    return await render_template('index.html', all_docs=all_docs)

@app.route('/create_collection/<collection_name>', methods=['POST'])
async def create_collection(collection_name):
    try:
        ObjectId(collection_name)
        return jsonify({'error': 'Collection name cannot be a valid ObjectId'})
    except Exception:
        db = db_helper.db
        if collection_name not in await db.list_collection_names():
            await db.create_collection(collection_name)
            redirect_url = url_for('index')
            return jsonify({'redirect_url': redirect_url})
        else:
            return jsonify({'error': 'Collection already exists'})

@app.route('/add_new_document/<collection_name>', methods=['POST'])
async def add_new_document(collection_name):
    try:
        data = await request.get_json()
        key = data.get('key')
        value = data.get('value')
        if not key or not value:
            return jsonify({'error': 'Key and value are required'})
        collection = db_helper.db[collection_name]
        new_document = {key: value}
        result = await collection.insert_one(new_document)
        if result.inserted_id:
            return jsonify({'success': 'New document added successfully', 'redirect_url': url_for('index')})
        return jsonify({'error': 'Failed to add a new document'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/add_key_value/<collection_name>/<document_id>', methods=['POST'])
async def add_key_value(collection_name, document_id):
    try:
        document_id = ObjectId(document_id)
    except Exception as e:
        print("Error converting document_id to ObjectId:", str(e))
        return jsonify({'error': 'Invalid document_id'})
    form_data = await request.form
    key = form_data.get('key')
    value = form_data.get('value')
    print(f"Received data: collection_name={collection_name}, document_id={document_id}, key={key}, value={value}")
    if key and value:
        collection = db_helper.db[collection_name]
        existing_document = await collection.find_one({'_id': document_id})
        if existing_document:
            await collection.update_one(
                {'_id': document_id},
                {'$set': {key: value}}
            )
            response_data = {
                    'message': f"Key-Value Pair '{key}':{value} added to Collection {collection_name} for document {document_id}",
                    'redirect_url': url_for('index')
                }
            return jsonify(response_data)
        else:
            return jsonify({'error': 'Document not found'})
    else:
        return jsonify({'error': 'Invalid parameters'})
        
@app.route('/edit_value/<string:collection_name>/<string:document_id>', methods=['PUT'])
async def edit_value(collection_name, document_id):
    try:
        data = await request.get_json()
        key_to_edit = data.get('keyToEdit')
        new_value = data.get('newValue')
        collection = db_helper.db[collection_name]
        document_id = ObjectId(document_id)
        query = {'_id': document_id}
        document = await collection.find_one(query)
        if document and key_to_edit in document:
            update_query = {'_id': document_id}
            update_data = {'$set': {key_to_edit: new_value}}
            await collection.update_one(update_query, update_data)
            return jsonify({'redirect_url': url_for('index')})
        return jsonify({'error': 'Document or key not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_document/<guild_id>/<document_id>', methods=[ 'DELETE'])
async def delete_document(guild_id, document_id):
    try:
        document_id = ObjectId(document_id)
    except Exception as e:
        print("Error converting document_id to ObjectId:", str(e))
        return jsonify({'error': 'Invalid document_id'})
    collection = db_helper.db[guild_id]
    existing_document = await collection.find_one({'_id': document_id})
    if existing_document:
        result = await collection.delete_one({'_id': document_id})
        redirect_url = url_for('index')
        return jsonify({'redirect_url': redirect_url})
    else:
        return jsonify({'error': 'Document not found'})

@app.route('/delete_key_value/<collection_name>/<document_id>', methods=['DELETE'])
async def delete_key_value(collection_name, document_id):
    try:
        document_id = ObjectId(document_id)
    except Exception as e:
        print("Error converting document_id to ObjectId:", str(e))
        return jsonify({'error': 'Invalid document_id'})
    form_data = await request.get_json()
    key_to_delete = form_data.get('keyToDelete')
    collection = db_helper.db[collection_name]
    existing_document = await collection.find_one({'_id': document_id})
    if existing_document and key_to_delete in existing_document:
        await collection.update_one(
            {'_id': document_id},
            {'$unset': {key_to_delete: 1}}
        )
        print(f"Key-Value Pair '{key_to_delete}' Deleted from Collection {collection_name} for document {document_id}")
        return jsonify({'redirect_url': url_for('index')})
    else:
        return jsonify({'error': 'Document or Key not found'})

@app.route('/delete_collection/<collection_name>', methods=['POST'])
async def delete_collection(collection_name):
    await db_helper.db.drop_collection(collection_name)
    redirect_url = url_for('index')
    print("Collection Deleted:", collection_name)  
    return jsonify({'redirect_url': redirect_url})

if __name__ == '__main__':
    app.run(debug=True)
