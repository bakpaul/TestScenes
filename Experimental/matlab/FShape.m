close all
clear all

Points = load('FPts.bin');

UpRightIDS = [339 347 281 273];
UpRight = Points(UpRightIDS,:);

MidRightIDS = [349 365 299 284];
MidRight = Points(MidRightIDS,:);

BottomIDS = [83 204 237 116];
Bottom = Points(BottomIDS,:);

UpRigh_m   = mean(UpRight)
MidRight_m = mean(MidRight)
Bottom_m   = mean(Bottom)
UpLeft_m   = [Bottom_m(1) UpRigh_m(2:3)]
MidLeft_m   = [Bottom_m(1) MidRight_m(2:3)]


Coord = [Bottom_m;
         MidLeft_m;
         MidRight_m;
         MidLeft_m;
         UpLeft_m;
         UpRigh_m]

plot3(Coord(:,1),Coord(:,2),Coord(:,3))
axis equal