import numpy as np

class ArcDetector:
    def __init__(self, img, threshold = 0.050):
        self.img = img
        self.min_Sradius = 3
        self.max_Sradius = 6
        self.min_Lradius = 4
        self.max_Lradius = 8
        self.Largecirlce_size = 20
        self.Smallcirlce_size = 16
        
        self.threshold = threshold
        self.border_lim = 4
        self.sae = np.zeros((2,self.img.shape[1], self.img.shape[0]))
        self.sae_lastest = np.zeros((2,self.img.shape[1], self.img.shape[0]))
        self.small_circle = np.array([
                                    [0, 3], [1, 3], [2, 2], [3, 1],
                                    [3, 0], [3, -1], [2, -2], [1, -3],
                                    [0, -3], [-1, -3], [-2, -2], [-3, -1],
                                    [-3, 0], [-3, 1], [-2, 2], [-1, 3]
                                ])
        self.large_circle = np.array([
                                    [0, 4], [1, 4], [2, 3], [3, 2],
                                    [4, 1], [4, 0], [4, -1], [3, -2],
                                    [2, -3], [1, -4], [0, -4], [-1, -4],
                                    [-2, -3], [-3, -2], [-4, -1], [-4, 0],
                                    [-4, 1], [-3, 2], [-2, 3], [-1, 4]
                                ])
    #event: t, x, y, pol
    def detect_corner(self,event):
        et, ex, ey,pol = event[0],int(event[1]), int(event[2]),int(event[3])
        pol_inv = 1 - pol
        t_last = self.sae_lastest[pol,ex,ey]
        t_last_inv = self.sae_lastest[pol_inv,ex,ey]

        # Filter blocks redundant spikes (consecutive and in short time) of the same polarity
        # This filter is required if the detector is to operate with corners with a majority of newest elements in the circles
        # Only when the polarity not the same as the last event or the time difference is larger than the threshold will the event be updated
        if((et > t_last + self.threshold) or (t_last_inv > t_last)):
            t_last = et
            self.sae[pol,ex,ey] = et
        else:
            t_last = et
            return False

        # Return if too close to the border
        if(ex < self.border_lim or ex >= (self.img.shape[1] - self.border_lim) or 
           ey < self.border_lim or ey >= (self.img.shape[0] - self.border_lim)):
            return False

        arc_right_idx = np.argmax(self.sae[pol,ex + self.small_circle[:,0],ey + self.small_circle[:,1]])
        segment_new_min_t = self.sae[pol,ex + self.small_circle[arc_right_idx,0],ey + self.small_circle[arc_right_idx,1]]

        arc_left_idx = (arc_right_idx-1+self.Smallcirlce_size) % self.Smallcirlce_size
        arc_right_idx = (arc_right_idx+1) % self.Smallcirlce_size

        arc_left_value = self.sae[pol,ex + self.small_circle[arc_left_idx,0],ey + self.small_circle[arc_left_idx,1]]
        arc_right_value = self.sae[pol,ex + self.small_circle[arc_right_idx,0],ey + self.small_circle[arc_right_idx,1]]
        arc_left_min_t = arc_left_value
        arc_right_min_t = arc_right_value
        # Expand
        # Initial expand does not require checking
        iter = 1
        while(iter < self.min_Sradius):
            if(arc_right_value > arc_left_value):
                if(arc_right_min_t < segment_new_min_t):
                    segment_new_min_t = arc_right_min_t
                # Expand arc  
                arc_right_idx= (arc_right_idx+1)%self.Smallcirlce_size
                arc_right_value = self.sae[pol,ex + self.small_circle[arc_right_idx,0],ey + self.small_circle[arc_right_idx,1]]
                if(arc_right_value < arc_right_min_t):
                    arc_right_min_t = arc_right_value
            else:
                if(arc_left_min_t < segment_new_min_t):
                    segment_new_min_t = arc_left_min_t
                # Expand arc 
                arc_left_idx = (arc_left_idx-1+self.Smallcirlce_size) % self.Smallcirlce_size
                arc_left_value = self.sae[pol,ex + self.small_circle[arc_left_idx,0],ey + self.small_circle[arc_left_idx,1]]
                if(arc_left_value < arc_left_min_t):
                    arc_left_min_t = arc_left_value
            iter += 1

        seg_size = self.min_Sradius

        while(iter < self.Smallcirlce_size):
            if(arc_right_value > arc_left_value):
                if(arc_right_value >= segment_new_min_t):
                    seg_size = iter + 1
                    if(arc_right_min_t < segment_new_min_t):
                        segment_new_min_t = arc_right_min_t

                # Expand arc
                arc_right_idx = (arc_right_idx+1)%self.Smallcirlce_size
                arc_right_value = self.sae[pol,ex + self.small_circle[arc_right_idx,0],ey + self.small_circle[arc_right_idx,1]]
                if(arc_right_value < arc_right_min_t):
                    arc_right_min_t = arc_right_value
            else:
                if(arc_left_value >= segment_new_min_t):
                    seg_size = iter + 1
                    if(arc_left_min_t < segment_new_min_t):
                        segment_new_min_t = arc_left_min_t

                # Expand arc
                arc_left_idx = (arc_left_idx-1+self.Smallcirlce_size) % self.Smallcirlce_size
                arc_left_value = self.sae[pol,ex + self.small_circle[arc_left_idx,0],ey + self.small_circle[arc_left_idx,1]]
                if(arc_left_value < arc_left_min_t):
                    arc_left_min_t = arc_left_value
            iter += 1
        if not (seg_size <= self.max_Sradius or 
            (seg_size >= (self.Smallcirlce_size - self.max_Sradius)) and
            (seg_size <= (self.Smallcirlce_size - self.min_Sradius))):
            return False
        
        # Expand large circle
        arc_right_idx = np.argmax(self.sae[pol,ex + self.large_circle[:,0],ey + self.large_circle[:,1]])
        segment_new_min_t = self.sae[pol,ex + self.large_circle[arc_right_idx,0],ey + self.large_circle[arc_right_idx,1]]

        arc_left_idx = (arc_right_idx-1+self.Largecirlce_size) % self.Largecirlce_size
        arc_right_idx = (arc_right_idx+1) % self.Largecirlce_size

        arc_left_value = self.sae[pol,ex + self.large_circle[arc_left_idx,0],ey + self.large_circle[arc_left_idx,1]]
        arc_right_value = self.sae[pol,ex + self.large_circle[arc_right_idx,0],ey + self.large_circle[arc_right_idx,1]]

        arc_right_min_t = arc_right_value
        arc_left_min_t = arc_left_value

        # Expand
        iter = 1
        while(iter < self.min_Lradius):
            if(arc_right_value > arc_left_value):
                if(arc_right_min_t < segment_new_min_t):
                    segment_new_min_t = arc_right_min_t
                # Expand arc  
                arc_right_idx= (arc_right_idx+1)%self.Largecirlce_size
                arc_right_value = self.sae[pol,ex + self.large_circle[arc_right_idx,0],ey + self.large_circle[arc_right_idx,1]]
                if(arc_right_value < arc_right_min_t):
                    arc_right_min_t = arc_right_value
            else:
                if(arc_left_min_t < segment_new_min_t):
                    segment_new_min_t = arc_left_min_t
                # Expand arc 
                arc_left_idx = (arc_left_idx-1+self.Largecirlce_size) % self.Largecirlce_size
                arc_left_value = self.sae[pol,ex + self.large_circle[arc_left_idx,0],ey + self.large_circle[arc_left_idx,1]]
                if(arc_left_value < arc_left_min_t):
                    arc_left_min_t = arc_left_value
            iter += 1

        seg_size = self.min_Lradius

        while(iter < self.Largecirlce_size):
            if(arc_right_value > arc_left_value):
                if(arc_right_value >= segment_new_min_t):
                    seg_size = iter + 1
                    if(arc_right_min_t < segment_new_min_t):
                        segment_new_min_t = arc_right_min_t

                # Expand arc
                arc_right_idx = (arc_right_idx+1)%self.Largecirlce_size
                arc_right_value = self.sae[pol,ex + self.large_circle[arc_right_idx,0],ey + self.large_circle[arc_right_idx,1]]
                if(arc_right_value < arc_right_min_t):
                    arc_right_min_t = arc_right_value
            else:
                if(arc_left_value >= segment_new_min_t):
                    seg_size = iter + 1
                    if(arc_left_min_t < segment_new_min_t):
                        segment_new_min_t = arc_left_min_t

                # Expand arc
                arc_left_idx = (arc_left_idx-1+self.Largecirlce_size) % self.Largecirlce_size
                arc_left_value = self.sae[pol,ex + self.large_circle[arc_left_idx,0],ey + self.large_circle[arc_left_idx,1]]
                if(arc_left_value < arc_left_min_t):
                    arc_left_min_t = arc_left_value
            iter += 1

        if not (seg_size <= self.max_Lradius or 
            (seg_size >= (self.Largecirlce_size - self.max_Lradius)) and
            (seg_size <= (self.Largecirlce_size - self.min_Lradius))):
            return False
        
        return True