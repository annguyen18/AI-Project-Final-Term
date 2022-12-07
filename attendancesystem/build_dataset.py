# USAGE
# python build_dataset.py --output dataset/huy
""" Xây dựng dataset bằng cách chụp webcam """
import argparse
import cv2
import os

# ap = argparse.ArgumentParser()
# ap.add_argument("-o", "--output", required=True, help="path to output directory")
# args = vars(ap.parse_args())

cd = os.getcwd()


def build(folderName):

    folder = cd + "\\" + "attendancesystem" + "\\" + "dataset" + "\\" + folderName
    try:
        os.mkdir(folder)
        video = cv2.VideoCapture(0)
        total = 0
        while True:
            ret, frame = video.read()

            cv2.imshow("video", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("k"):
                # điền thêm số 0 bên trái cho đủ 5 kí tự
                p = os.path.sep.join(
                    [folder, "{}.png".format(str(total).zfill(5))])
                cv2.imwrite(p, frame)
                total += 1
                # nhấn q để thoát
            elif key == ord("q"):
                break

        print("[INFO] {} face images stored".format(total))
        video.release()
        cv2.destroyAllWindows()
    except:
        print("Sinh viên đã tồn tại.")
