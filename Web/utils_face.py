from PIL import Image
import numpy as np
import dlib

face_detector = dlib.get_frontal_face_detector()

shape_predictor_5_point = dlib.shape_predictor("models/shape_predictor_5_face_landmarks.dat")
shape_predictor_68_point = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")

face_encoder = dlib.face_recognition_model_v1("models/dlib_face_recognition_resnet_model_v1.dat")
taguchi_face_encoder = dlib.face_recognition_model_v1("models/taguchi_face_recognition_resnet_model_v1.dat")

def load_image_file(file, mode='RGB'):
   """
   Loads an image file (.jpg, .png, etc) into a numpy array

   :param file: image file name or file object to load
   :param mode: format to convert the image to. Only 'RGB' (8-bit RGB, 3 channels) and 'L' (black and white) are supported.
   :return: image contents as numpy array
   """
   im = Image.open(file)
   if mode:
      im = im.convert(mode)
   return np.array(im)

def _rect_to_css(rect):
    """
    Convert a dlib 'rect' object to a plain tuple in (top, right, bottom, left) order

    :param rect: a dlib 'rect' object
    :return: a plain tuple representation of the rect in (top, right, bottom, left) order
    """
    return rect.top(), rect.right(), rect.bottom(), rect.left()

def _css_to_rect(css):
    """
    Convert a tuple in (top, right, bottom, left) order to a dlib `rect` object

    :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
    :return: a dlib `rect` object
    """
    return dlib.rectangle(css[3], css[0], css[1], css[2])

def _trim_css_to_bounds(css, image_shape):
    """
    Make sure a tuple in (top, right, bottom, left) order is within the bounds of the image.

    :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
    :param image_shape: numpy shape of the image array
    :return: a trimmed plain tuple representation of the rect in (top, right, bottom, left) order
    """
    return max(css[0], 0), min(css[1], image_shape[1]), min(css[2], image_shape[0]), max(css[3], 0)

def _raw_face_locations(img, number_of_times_to_upsample=1, model="hog"):
    """
    Returns an array of bounding boxes of human faces in a image

    :param img: An image (as a numpy array)
    :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
    :param model: Which face detection model to use. "hog" is less accurate but faster on CPUs. "cnn" is a more accurate
                  deep-learning model which is GPU/CUDA accelerated (if available). The default is "hog".
    :return: A list of dlib 'rect' objects of found face locations
    """
    return face_detector(img, number_of_times_to_upsample)

def face_locations(img, number_of_times_to_upsample=1, model="hog"):
    """
    Returns an array of bounding boxes of human faces in a image

    :param img: An image (as a numpy array)
    :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
    :param model: Which face detection model to use. "hog" is less accurate but faster on CPUs. "cnn" is a more accurate
                  deep-learning model which is GPU/CUDA accelerated (if available). The default is "hog".
    :return: A list of tuples of found face locations in css (top, right, bottom, left) order
    """
    return [_trim_css_to_bounds(_rect_to_css(face), img.shape) for face in _raw_face_locations(img, number_of_times_to_upsample, model)]


def _raw_face_landmarks(face_image, face_locations=None, model="large"):
    if face_locations is None:
        face_locations = _raw_face_locations(face_image)
    else:
        face_locations = [_css_to_rect(face_location) for face_location in face_locations]

    pose_predictor = shape_predictor_68_point

    if model == "small":
        pose_predictor = shape_predictor_5_point

    return [pose_predictor(face_image, face_location) for face_location in face_locations]

def face_encodings(face_image, known_face_locations=None, num_jitters=1):
    """
    Given an image, return the 128-dimension face encoding for each face in the image.

    :param face_image: The image that contains one or more faces
    :param known_face_locations: Optional - the bounding boxes of each face if you already know them.
    :param num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
    :param model: Optional - which model to use. "large" (default) or "small" which only returns 5 points but is faster.
    :return: A list of 128-dimensional face encodings (one for each face in the image)
    """
    print("Encoding faces..")
    raw_landmarks = _raw_face_landmarks(face_image, known_face_locations)
    return [np.array(face_encoder.compute_face_descriptor(face_image, raw_landmark_set, num_jitters)) for raw_landmark_set in raw_landmarks]


def hitung_wajah(foto):
   print("Hitung faces...")
   # Count faces on single image
   print("Loading image...")
   image = load_image_file(foto)
   print("Locating faces...")
   locations = face_locations(image)
   print("lcoations: ", locations)
   print("Face located")
   jumlah_wajah = len(locations)
   print(jumlah_wajah)
   if jumlah_wajah == 1: # Crop
      top, right, bottom, left = locations[0]
      
      faceImage = image[top:bottom, left:right]
      final = Image.fromarray(faceImage)
    
      return (True, final, image, locations)
   elif jumlah_wajah > 1:
      return (False, "jumlah wajah lebih dari 1")
   return (False, "tidak ditemukan satupun wajah")


def face_distance(face_encodings, face_to_compare):
   """
   Given a list of face encodings, compare them to a known face encoding and get a euclidean distance
   for each comparison face. The distance tells you how similar the faces are.

   :param faces: List of face encodings to compare
   :param face_to_compare: A face encoding to compare against
   :return: A numpy ndarray with the distance for each face in the same order as the 'faces' array
   """
   if len(face_encodings) == 0:
      return np.empty((0))

   return np.linalg.norm(face_encodings - face_to_compare, axis=1)

def compare_faces(known_face_encodings, face_encoding_to_check, tolerance=0.6):
   """
   Compare a list of face encodings against a candidate encoding to see if they match.

   :param known_face_encodings: A list of known face encodings
   :param face_encoding_to_check: A single face encoding to compare against the list
   :param tolerance: How much distance between faces to consider it a match. Lower is more strict. 0.6 is typical best performance.
   :return: A list of True/False values indicating which known_face_encodings match the face encoding to check
   """
   return list(face_distance(known_face_encodings, face_encoding_to_check) <= tolerance)

def compare_faces_2(known_face_encodings, face_encoding_to_check, tolerance=0.6):
    distances = face_distance(known_face_encodings, face_encoding_to_check)

    if True in tuple(distances <= tolerance):
        return np.argmin(distances)
    else:
        return False
    
def compare_faces_3(known_face_encodings, face_encoding_to_check, tolerance=0.50):
    print(f"Seeking nearest...")
    distances = face_distance(known_face_encodings, face_encoding_to_check)
    print(f"Distances: {distances}")
    print(f"Average Distance: {np.average(distances)}")

    if np.average(distances) > tolerance:
        return False
    else:
        return True

def compare_wajah(list_encodes):
   list = list_encodes.copy()
   p = list.pop(0)
   
   result = compare_faces(list, p)
   if False in result:
      return False
   return True

def compare_wajah_2(list_encodes, encode):
   new_list = list_encodes.copy()
   new_encode = encode.copy()
   
   result = compare_faces(new_list, new_encode, 0.6)
   if False in result:
      return False
   return True