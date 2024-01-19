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

@app.route('/delete/<document_id>')
async def delete(document_id):
    print("Received document_id:", document_id)
    
    # Convert the string document_id to ObjectId
    document_id = ObjectId(document_id)
    existing_document = await db_helper.db.documents.find_one({'_id': document_id})
    if existing_document:
        result = await db_helper.db.documents.delete_one({'_id': document_id})
        print("Delete Result:", result)
    else:
        print("Document not found:", document_id)

    redirect_url = url_for('index')
    return jsonify({'redirect_url': redirect_url})


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
