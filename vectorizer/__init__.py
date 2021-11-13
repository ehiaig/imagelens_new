from vectorizer.img_2_vec import Img2Vec
from PIL import Image
import requests
import cv2
from sklearn.metrics.pairwise import cosine_similarity

class ImageVectorizer():

    def __init__(self):
        self.img2vec = Img2Vec()

    def vectorizeImage(self, file_path=None, url=None, pil_image=None, opencv_image=None):

        image = None

        if file_path is not None:
            image = Image.open(file_path)
        elif url is not None:
            image = self.get_image_from_url(url)
        elif pil_image is not None:
            image = pil_image
        elif opencv_image is not None:
            image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)

        vector_512 = self.img2vec.get_vec(image)

        return vector_512
    
    def get_image_from_url(self, url):
        try:
            print("Downloading " + url + " ....")
            pil_image = Image.open(requests.get(url, stream=True).raw)
            return pil_image
        except:
            raise ValueError("Image URL not valid for " + url)

    
    def get_similarity(self, vector1, vector2):
        similarity = cosine_similarity(vector1.reshape((1, -1)), vector2.reshape((1, -1)))[0][0]
        return similarity
            
