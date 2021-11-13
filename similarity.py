import os
from PIL import Image
import json
from random import randint
from flask import make_response, abort
from config import db
from models import Vector, VectorSchema
import connexion
from vectorizer import ImageVectorizer
from utils import ApiError
import boto3
from io import BytesIO
from sklearn.metrics.pairwise import cosine_similarity
import ast
import pickle
import numpy
vector_generator = ImageVectorizer() 
vector_schema = VectorSchema()
session = boto3.session.Session()
client = session.client(
    's3',
    region_name=os.getenv("REGION_NAME"),
    endpoint_url=os.getenv("ENDPOINT_URL"),
    aws_access_key_id=os.getenv('SPACES_KEY'),
    aws_secret_access_key=os.getenv('SPACES_SECRET')
)


def p_get_one(vector_id):
    result = get_one(vector_id)
    return {
        "type": "object",
        "message": "Vectors retrieved",
        "data" : result
    }


def p_get_all():
    result = get_all()
    return {
        "type": "object",
        "message": "Vectors retrieved",
        "data" : result
    }


def get_all():
    vectors = Vector.query.order_by().all()
    vectors_schema = VectorSchema(many=True)
    return vectors_schema.dump(vectors)

def get_one(vector_id):
    
    # Build the initial query
    vector = Vector.query.filter_by(vector_id=vector_id).first()

    if vector is not None:
        # Serialize the the response data 
        data = vector_schema.dump(vector)
        return data
    else:
        abort(404, f"Vector not found for Id: {vector_id}")


def p_create_vector(body):
    image_url = body.get("image_url") or None
    misc = body.get("misc") or None
    image_files = connexion.request.files
    image_file = image_files['image_file'] if image_files else None
    vector_id = randint(10000000, 99999999)
    encoding = None
    vector_result = None
    if image_url is None and image_file is None:
        raise ApiError(
            "Supply a valid value for image_url or image_file.",
            "invalid_data",
        )
    
    if image_url is not None:
        vector_result = vector_generator.vectorizeImage(url=image_url)
        encoding = {
            "encoded_vector": vector_result.tolist()
        }
        encoding = json.dumps(encoding)
    
    if image_file is not None:
        image_url = upload_input_image(image_file.read(), image_file)
        vector_result = vector_generator.vectorizeImage(file_path=image_file)
        encoding = {
            "encoded_vector": vector_result.tolist()
        }
        encoding = json.dumps(encoding)

    new_vector = Vector(
        vector_id=vector_id,
        encoding=encoding,
        misc=misc,
        image_url=image_url,
        image_byte=pickle.dumps(vector_result)
    )

    db.session.add(new_vector)
    db.session.commit()

    result = get_one(new_vector.vector_id)
    return {
        "type": "object",
        "message": "Vector generated",
        "data" : result
    }


def p_delete(vector_id):
    vector = Vector.query.filter(vector_id == vector_id).first()
    if vector is not None:
        db.session.delete(vector)
        db.session.commit()
        return {
            "type": "object",
            "message": "Vectors deleted",
            # "data" : vector_id
        }
        # return make_response(f"vector {vector_id} deleted", 201)
    else:
        abort(404, f"vector not found for Id: {vector_id}")


def upload_input_image(file_path, input_file_name=None):
    output_io = BytesIO(file_path)
    pil_image = Image.open(output_io)
    pil_image.save(output_io,format="jpeg")
    file_data = output_io.getvalue()
    client.put_object(
        Bucket=os.getenv("SPACE_NAME"),
        Key=input_file_name.filename,
        Body=file_data,
        ServerSideEncryption='AES256',
        ACL='public-read'
    )
    url = download_image_url(input_file_name.filename)
    return url


def download_image_url(file_name):
    url = client.generate_presigned_url('get_object', Params = {'Bucket': os.getenv("SPACE_NAME"), 'Key': file_name})
    return url

def p_similar_images(body):
    generated_vector = p_create_vector(body)
    encoding = generated_vector["data"]["encoding"]
    dict_encoding = ast.literal_eval(encoding)
    encoded_vector = dict_encoding["encoded_vector"]
    similar_images = []

    all_vectors = get_all()
    
    for vector in all_vectors:
        
        vector_encoding = vector["encoding"]
        dict_encoding = ast.literal_eval(vector_encoding)
        vector = dict_encoding["encoded_vector"]

        similarity = vector_generator.get_similarity(numpy.fromstring(encoded_vector), numpy.fromstring(vector))

        if similarity >= 0.80:
            similar_images.append(vector)

    return similar_images

def p_similar_images_new(body):
    generated_vector = p_create_vector(body)
    encoding = generated_vector["data"]["image_byte"]
    similar_images = []

    all_vectors = get_all()
    
    for vector in all_vectors:
        
        vector_encoding = vector["image_byte"]
        similarity = vector_generator.get_similarity(numpy.fromstring(encoding, dtype=int), numpy.fromstring(vector_encoding, dtype=int))
        print("Simiiii type", type(similarity))
    #     if similarity >= 0.80:
    #         similar_images.append(vector)

    # return similar_images