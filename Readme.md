# Arc*: Asynchronous Event-based Corner Detection 
This code is a reimplementation of the Arc* algorithm described in the paper  "**Asynchronous Corner Detection and Tracking for Event Cameras in Real Time**", Alzugaray & Chli, RA-L 2018. This work was developed at the [Vision for Robotics Lab](http://v4rl.ethz.ch/), [ETH Zurich](http://ethz.ch/).


# Reference:
The code of detector is mainly reference and reimplement from this [github](https://github.com/ialzugaray/arc_star_ros), but in a python fashion. The implementation includes Arc detector and Arc tracker and it does not require the usage of ROS. The plot is from matplotlib package directly drawing events on the image frames. 

# How to use the code
Clone the repository and compile the project:

    $ git clone https://github.com/ialzugaray/arc_star_ros.git
    $ python read_event.py 

You can use the event text files from the the [Event Camera Dataset](http://rpg.ifi.uzh.ch/davis_data.html)
