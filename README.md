**Running Script**

To run the program, build the docker image using the following terminal commands:

```
docker build -t dali_barnacles .
```

```
docker run -p 8050:8050 --rm dali_barnacles
```

**Documentation**

My thought-process generally follows this:
1. My goal here wasn't necessarily to create a fully unsupervised model with complete hyperparameter tuning. While that would be really nice, I realised that
there could be a lot of variability between barnacle images, and having a one-size-fits-all model would be very hard to do. I just needed to find a way to count barnacles and do a pretty good job, but have a visual component that allows a human to quickly check how the model is doing.

2. I thought of the task as being comprised of two components (which is reflected in my code as well): a backend and a frontend. The backend is made up of a preprocessing component (that crops the image and prepares for edge detection and finding contours) and an analysis component (that actually finds and counts the contours/barnacles). The frontend and the backend talk to one another - the user is able to choose an image in the frontend GUI, which sends it to the backend, performs canny edge detection and counts the barnacles, overlays the mask on the image, and returns the two to the frontend for the user to see. 
    
3. In terms of evaulating performance, and what metrics I care about, it really depends on the client's priorities and what they're using this model for. If it's bad to have false positives, then focusing on <ins>Precision</ins> might be a good idea (how many times does my model think there is a barnacle when there actually isn't one). If it isn't terrible to have false positives, but the client really wants to know where there is a barnacle, then looking at <ins>Recall</ins> might be a better choice. A good "overall" metric that would balance the two concerns would be an <ins>F1 score</ins>. Getting a sense of the clients goals would help further tune the model and increase accuracy depending on the use case. It would be good to know how many barnacles are actually in the image, so one way that I could've done that is by doing edge detection/finding contours on the provided mask (if available). This would help me get a sense of how the model is doing.

4. I first performed some basic preprocessing on the image, with color thresholds, some morphological operations, edge detection, and then cropping (slicing). I used adaptive thresholding to take into account the variations in lighting in the images. I performed canny edge detection on the barnacles, cleaned up the edges a little bit, and then filtered the detected contours based their area and roundness. A variety of hyperparameters as well as the final result (masked image and barnacle count) are displayed on a GUI.

5. From the looks of it I've gotten most of the barnacles, missed a few, but then double counted some as well. If my thought-process is correct there's roughly 1900 barnacles in the first image, I correctly identified ~90% of them, and doublecounted/misidentified 10-20% of the 2370 that I detected.
    
6. I think this process is definitely worth pursuing. I would refine my backend more, I think I could apply some more morphological operations to clean up some of the detected edges a bit and close some of the gaps more. The visual component of the prototype tells me a lot about what/how hyperparameters are affecting the accuracy - I think being a little more "picky" with the roundness of counted barnacles might help a little bit. There is definitely a lot of work left to do on this, it is by no means finished, but hopefullly this gives a little taste of how  I think about things, and my overall "style" of coding.

7. Playing around with different edge detection algorithms/models was pretty fun - it was definitely challenging finding one that would accuractly pick out objects that were so small and densely clustered together in the image. Finding something that worked decently well was both a surprise and an exciting outcome!
