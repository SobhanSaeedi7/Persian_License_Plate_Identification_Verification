import argparse
import cv2
import pandas

from difflib import SequenceMatcher
from ultralytics import YOLO

from database import Database
from deep_text_recognition_benchmark.dtrb import DTRB



parser = argparse.ArgumentParser()

# parser.add_argument('--image_folder', required=True, help='path to image_folder which contains text images')

parser.add_argument('--workers', type=int, help='number of data loading workers', default=0)

parser.add_argument('--batch_size', type=int, default=192, help='input batch size')

# parser.add_argument('--saved_model', required=True, help="path to saved_model to evaluation")

""" Data processing """

parser.add_argument('--batch_max_length', type=int, default=25, help='maximum-label-length')

parser.add_argument('--imgH', type=int, default=32, help='the height of the input image')

parser.add_argument('--imgW', type=int, default=100, help='the width of the input image')

parser.add_argument('--rgb', action='store_true', help='use rgb input')

parser.add_argument('--character', type=str, default='0123456789abcdefghijklmnopqrstuvwxyz', help='character label')

parser.add_argument('--sensitive', action='store_true', help='for sensitive character mode')

parser.add_argument('--PAD', action='store_true', help='whether to keep ratio then pad for image resize')

""" Model Architecture """

parser.add_argument('--Transformation', type=str, default="TPS", help='Transformation stage. None|TPS')

parser.add_argument('--FeatureExtraction', type=str, default="ResNet", help='FeatureExtraction stage. VGG|RCNN|ResNet')

parser.add_argument('--SequenceModeling', type=str, default="BiLSTM", help='SequenceModeling stage. None|BiLSTM')

parser.add_argument('--Prediction', type=str, default="Attn", help='Prediction stage. CTC|Attn')

parser.add_argument('--num_fiducial', type=int, default=20, help='number of fiducial points of TPS-STN')

parser.add_argument('--input_channel', type=int, default=1, help='the number of input channel of Feature extractor')

parser.add_argument('--output_channel', type=int, default=512,

                    help='the number of output channel of Feature extractor')

parser.add_argument('--hidden_size', type=int, default=256, help='the size of the LSTM hidden state')

parser.add_argument("--detector-weights", type=str, default="weights/yolov8-detector/yolov8-s-license-plate-detector.pt")

parser.add_argument("--recognizer-weights", type=str, default="weights/dtrb-recognizer/dtrb-None-VGG-BiLSTM-CTC-license-plate-recognizer.pth")

parser.add_argument("--dataset", type=str, default="license_plates.db")

parser.add_argument("--input-image", type=str, default="io/input/IMG_5178.JPG")

parser.add_argument("--threshold", type=float, default=0.6)
parser.add_argument("--verification_mode", action='store_true', help='Verification The License Plates')
parser.add_argument("--editor-mode", action='store_true', help='Edit Plates Dataset after Verifying')
opt = parser.parse_args()


database = Database(opt.dataset)

plate_detector = YOLO(opt.detector_weights)
plate_recognizer = DTRB(opt.recognizer_weights, opt)


image = cv2.imread(opt.input_image)
results = plate_detector.predict(image)

for result in results:

    for i in range(len(result.boxes.xyxy)):

        if result.boxes.conf[i] > opt.threshold:

            bbox_tensor = result.boxes.xyxy[i]

            bbox_ndarray = bbox_tensor.cpu().detach().numpy().astype(int)

            x1, y1, x2, y2 = bbox_ndarray

            plate_image = image[y1:y2, x1:x2].copy()


            cv2.imwrite(f"io/output/plate_image_result_{i}.jpg", plate_image)

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 4)
            

            plate_image = cv2.resize(plate_image, (100, 32))

            plate_image = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
            plate = plate_recognizer.predict(plate_image, opt)
            
            dataset = database.show_plates()

            if opt.verification_mode:
                for i in dataset:
                    check_in = False
                    if SequenceMatcher(None, i[1], plate).ratio() > 0.8:
                        print(True)
                        check_in = True
                        break
                if check_in == False:
                    print(False)
            
            if opt.verification_mode and opt.editor_mode:
                for i in dataset:
                    if SequenceMatcher(None, i[1], plate).ratio() > 0.8:
                        action = input('This License has already been registered.\nDelete(D), Show Data List(S), Exit(anything else) : ')
                        
                if check_in == False:
                    action = input('This License Plate isn`t registered!\nAdd(A), Show Data List(S), Exit(anything else) : ')
                    break
                if action == 'S':
                    plates = database.show_plates()
                    column = ['Plate Owner', 'License Plate'] 
                    df = pandas.DataFrame(plates, columns=column)
                    print(df)

                elif action == 'A':
                    owner = input('Enter owner name : ')
                    database.add_new(owner, plate)
                    plates = database.show_plates()
                    column = ['Plate Owner', 'License Plate'] 
                    df = pandas.DataFrame(plates, columns=column)
                    print(df)

                elif action == 'D':
                    database.remove_plate(plate)
                    plates = database.show_plates()
                    column = ['Plate Owner', 'License Plate'] 
                    df = pandas.DataFrame(plates, columns=column)
                    print(df)



cv2.imwrite("io/output/image_result.jpg", image)