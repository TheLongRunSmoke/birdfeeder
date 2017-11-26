import numpy as np
import cv2

cap = cv2.VideoCapture(0)

for i in range(0,18):
    print('%d : %f' % (i, cap.get(i)))

cap.set(3,320)
cap.set(4,240)
cap.set(15,0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
