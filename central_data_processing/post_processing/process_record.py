import face_recognition
from sklearn.decomposition import TruncatedSVD
from sklearn import preprocessing
import numpy as np
import pickle
import psycopg2
import hashlib
import time
#import cv2

class ProcessRecord:
    def __init__(self, test=False):
        self.host='fink-security.c82uau1daq0n.us-east-1.rds.amazonaws.com'
        self.user='officerfink'
        self.passwd='thefinkdoesnotblink'
        self.database='fink_security'
        self.port_num=5432
        self.testMode = test
        self.recordSwitch = {
            'image':self.image,
            'lp':self.lp,
            'mac':self.mac
        }

    def process(self,recordType, recordData):
        self.recordSwitch[recordType](recordData)

    ## process_image
    def image(self,recordData):
        ### encode
        faceEmbedding = self.embed_face(recordData['img'])

        #build record hash from unit / timestamp
        m = hashlib.md5()
        m.update(recordData['unit_hash'].encode('utf8'))
        m.update(u'{0!s}'.format(time.time()).encode('utf-8'))
        recordHash = m.hexdigest()

        #build resource hash from record_hash / 01: placeholder for multiple faces per record
        m = hashlib.md5()
        m.update(recordHash.encode('utf8'))
        m.update(u'{0!s}'.format(1).encode('utf-8'))
        resourceHash = m.hexdigest()

        self.db_connect()
        ### identify closest entity (0 if new): once we have sufficient samples
        self.cursor.execute('insert into public.records ( record_hash,  unit_hash) VALUES(%s, %s) ', (recordHash,recordData['unit_hash']))
        self.cursor.execute('insert into public.faces ( resource_hash, record_hash, embedding) VALUES( %s, %s, cube(%s)) ', (resourceHash, recordHash,faceEmbedding.tolist()))

        self.db_finish()

    ## process_lp
    def lp(self,recordData):
        pass

    ## process_mac
    def mac(self,recordData):
        pass

    ## Face encoding (note, 100 dimension encoding for postgresql indexing
    def embed_face(self,newFace):
        newFaceEmbedding = face_recognition.face_encodings(newFace)[0].reshape(1, -1)
        svdFaceEmbedding = self.SVD(newFaceEmbedding)
        svdFaceEmbeddingNorm = preprocessing.normalize(svdFaceEmbedding, norm='l2')
        return svdFaceEmbeddingNorm


    def db_connect(self):
        self.connection = psycopg2.connect(host=self.host, user=self.user, password=self.passwd, dbname=self.database, port=self.port_num)
        self.cursor = self.connection.cursor()

    def db_finish(self):
        self.connection.commit()
        self.connection.close()


    def SVD(self,X):
        transformer = pickle.load(open('faces.pickle', 'rb'))
        svdX = transformer.transform(X)
        return svdX

    def lst2pgarr(alist):
        return '{' + ','.join(alist) + '}'

    #create initial svd model for embedding: replace with captcured images
    def makeSVD(self):
        images = np.array(
                [
                face_recognition.face_encodings(face_recognition.load_image_file('/home/chrisc/Pictures/faces/f0.jpg'))[0],
                face_recognition.face_encodings(face_recognition.load_image_file('/home/chrisc/Pictures/faces/f1.jpg'))[0],
                face_recognition.face_encodings(face_recognition.load_image_file('/home/chrisc/Pictures/faces/f2.jpg'))[0],
                face_recognition.face_encodings(face_recognition.load_image_file('/home/chrisc/Pictures/faces/f3.jpg'))[0],
                face_recognition.face_encodings(face_recognition.load_image_file('/home/chrisc/Pictures/faces/f4.jpg'))[0],
                face_recognition.face_encodings(face_recognition.load_image_file('/home/chrisc/Pictures/faces/f5.jpg'))[0],
                face_recognition.face_encodings(face_recognition.load_image_file('/home/chrisc/Pictures/faces/f6.jpg'))[0],
                face_recognition.face_encodings(face_recognition.load_image_file('/home/chrisc/Pictures/faces/f7.jpg'))[0],
                face_recognition.face_encodings(face_recognition.load_image_file('/home/chrisc/Pictures/faces/f8.jpg'))[0],
                face_recognition.face_encodings(face_recognition.load_image_file('/home/chrisc/Pictures/faces/f9.jpg'))[0]
        ]
        )
        print(images.shape)
        transformer = TruncatedSVD(algorithm='randomized', n_components=100, random_state=1)
        transformer.fit(images)
        a=transformer.transform(images[0])
        pickle.dump(transformer, open('faces.pickle', 'wb'))
        print('done')

    # Clustering

    #stabalize current recognition


# How to test / generate all test image embeddings
# clustering?
# postgresql connections: save original
# re-model / pickle / recluster


def main(test=False):
    recordHandler = ProcessRecord(test)
    if test:
        #recordHandler.makeSVD()
        img =  face_recognition.load_image_file('/home/chrisc/Pictures/faces/f0.jpg')
        recordHandler.process('image',{'img':img,'unit_hash':u'dc5c7986daef50c1e02ab09b442ee34f'})

if __name__ == '__main__':
    main(True)