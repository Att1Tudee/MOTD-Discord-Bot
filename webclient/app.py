# app.py
from quart import Quart, make_response, render_template, request, jsonify, url_for, redirect
from dbhelper import Dbhelper
from bson import ObjectId

app = Quart(__name__)
db_helper = Dbhelper()

@app.route('/')
async def index():
    # Get all collection names
    collection_names = await db_helper.db.list_collection_names()

    # Retrieve documents from each collection
    all_docs = {}
    for collection_name in collection_names:
        documents = await db_helper.db[collection_name].find().to_list(length=100)
        all_docs[collection_name] = documents
    return await render_template('index.html', all_docs=all_docs)

@app.route('/add', methods=['POST'])
async def add():
    document_data = await request.form.get('document_data')
    await db_helper.db.documents.insert_one({'data': document_data})
    print("Document Added:", document_data)  # Add this line for debugging
    return await redirect(url_for('index'))

@app.route('/delete/<guild_id>/<document_id>', methods=[ 'DELETE'])
async def delete(guild_id, document_id):
    print("Received guild_id:", guild_id)
    print("Received document_id:", document_id)

    try:
        # Convert the string document_id to ObjectId
        document_id = ObjectId(document_id)
        print("Converted to ObjectId:", document_id)
    except Exception as e:
        print("Error converting document_id to ObjectId:", str(e))
        return jsonify({'error': 'Invalid document_id'})

    collection = db_helper.db[guild_id]
    existing_document = await collection.find_one({'_id': document_id})
    print("Existing Document:", existing_document)

    if existing_document:
        result = await collection.delete_one({'_id': document_id})
        print("Delete Result:", result)
        redirect_url = url_for('index')
        return jsonify({'redirect_url': redirect_url})
    else:
        print("Document not found:", document_id)
        return jsonify({'error': 'Document not found'})

@app.route('/delete_collection/<collection_name>', methods=['POST'])
async def delete_collection(collection_name):
    # Delete the collection
    await db_helper.db.drop_collection(collection_name)
    
    # Return JSON response with redirect URL
    redirect_url = url_for('index')
    print("Collection Deleted:", collection_name)  # Add this line for debugging
    return jsonify({'redirect_url': redirect_url})

if __name__ == '__main__':
    app.run(debug=True)
