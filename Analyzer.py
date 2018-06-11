import json
import re
import numpy as np
import matplotlib.pyplot as plt


# variables

# file location
json_addr = "H:\\human recorder raw\\05210101.json"
# plot settings
# devide by ','.
# M/F/B: male, female, both; H/J0-J24: head, joint number; Ro/Pi/Ya/X/Y/Z: roll, pitch, yaw, x, y, z;
plot_attr = "F,H,Ya"


# plot
def plot(humans, joints, dimensions):
    pass


# class to store data per human
class Human:
    def __init__(self, trackingId):
        self.trackingId = trackingId
        self.gender = 'not assigned'
        # head dir
        self.roll = []
        self.pitch = []
        self.yaw = []
        # joints
        self.joint_0 = []
        self.joint_1 = []
        self.joint_2 = []
        self.joint_3 = []
        self.joint_4 = []
        self.joint_5 = []
        self.joint_6 = []
        self.joint_7 = []
        self.joint_8 = []
        self.joint_9 = []
        self.joint_10 = []
        self.joint_11 = []
        self.joint_12 = []
        self.joint_13 = []
        self.joint_14 = []
        self.joint_15 = []
        self.joint_16 = []
        self.joint_17 = []
        self.joint_18 = []
        self.joint_19 = []
        self.joint_20 = []
        self.joint_21 = []
        self.joint_22 = []
        self.joint_23 = []
        self.joint_24 = []


def pick_human(humans, trackingId):
    for human in humans:
        if trackingId == human.trackingId:
            return human
    # return untracked human if no matches
    return humans[0]


def main():
    # 1. load

    # separate each object
    # decode error: only one json object each file. one pair of {}.
    json_objects = []
    # r: read only, w: write only!!! DO NOT use w!!!
    with open(json_addr, 'r') as f:
        bracket_stack = 0
        json_obj = []
        for line in f:
            line = line.rstrip()
            if line[-1] == '{':
                bracket_stack += 1
            if line[-1] == '}':
                bracket_stack -= 1
            # may end with '},'
            if len(line) >= 2 and line[-2] == '}':
                bracket_stack -= 1
            json_obj.append(line)
            if bracket_stack == 0:
                json_objects.append(json_obj)
                # list.clear() clears list element in list as well.
                json_obj = []

    # parse each object
    json_rawdata = []
    for obj in json_objects:
        obj_str = '\n'.join(obj)
        # load: file-like obj, loads: str, bytes, bytearray
        rawdata = json.loads(obj_str)
        json_rawdata.append(rawdata)

    assert len(json_objects) == len(json_rawdata)
    frame_num = len(json_rawdata) - 1
    print('frame number: ' + str(frame_num))

    # 2. extract & store

    # start timestamp
    if 'start time' not in json_rawdata[0]:
        raise ValueError('time stamp missing')
    start_time = json_rawdata[0]['start time']
    print('json file starts at: ' + str(start_time))
    del json_rawdata[0]

    # traverse through each frame
    # TODO fill the other one if body count = 1
    id_list = []
    humans = [Human(0)]
    for frame in json_rawdata:
        # check body count
        body_count = len(frame['people'])

        if body_count == 0:
            continue

        for n in range(body_count):
            # tracking ID, human struct
            trackingId = 0
            if 'trackingId' in frame['people'][n]:
                trackingId = frame['people'][n]['trackingId']
            if trackingId not in id_list:
                id_list.append(trackingId)
                humans.append(Human(trackingId))
                print(f'created human with id: {trackingId}')

            human = pick_human(humans, trackingId)

            # head orientation: pitch yaw roll
            pitch, yaw, roll = (0.0, 0.0, 0.0)  # when no data
            if 'head dir' in frame['people'][n]:
                pitch, yaw, roll = (float(degree) for degree in frame['people'][n]['head dir'].split(','))
            human.pitch.append(pitch)
            human.roll.append(roll)
            human.yaw.append(yaw)

            # joints: 0 - 24
            for joint in range(25):
                joint_value = [0.0] * 6
                if str(joint) in frame['people'][n]:
                    joint_value = frame['people'][n][str(joint)]
                value_list = human.__getattribute__('joint_' + str(joint))
                value_list.append(joint_value)

    # 3. gender

    # use average position of head joint.
    # get most longest two human instances, suggest they are valid subjects.
    if len(humans) < 2:
        raise IndexError('less than 2 humans.')
    humans.sort(key=lambda x: len(x.joint_3), reverse=True)
    person1 = humans[0]
    person2 = humans[1]
    # get horizontal coordinates of head joint
    person1_data = [person1.joint_3[i][1] for i in range(len(person1.joint_3))]
    person2_data = [person2.joint_3[i][1] for i in range(len(person2.joint_3))]
    if sum(person1_data) / len(person1_data) < sum(person2_data) / len(person2_data):
        person1.gender = 'female'
        person2.gender = 'male'
    else:
        person1.gender = 'male'
        person2.gender = 'female'

    # 4. plot

    # head dir
    plot_re = re.compile(plot_attr)


if __name__ == '__main__':
    main()
