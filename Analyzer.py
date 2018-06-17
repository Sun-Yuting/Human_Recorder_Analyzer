import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import pickle


# variables

# file location
json_addr = "H:\\human recorder raw\\05210101.json"
# plot settings
use_plot = False
# devide by ','.
# M/F/B: male, female, both; H/J0-J24: head, joint number; Ro/Pi/Ya/X/Y/Z: roll, pitch, yaw, x, y, z;
plot_pattern = "F,H,RoPiYa"
interp_pattern = "F,H,Ya"


# plot
def plot(humans, joints, dimensions, interpolation=None):
    if len(humans) * len(joints) * len(dimensions) == 0:
        raise IndexError('empty plot parameter.')
    # get data
    for human in humans:
        for joint in joints:
            for dimension in dimensions:
                if joint == 'H':
                    if dimension in ['x', 'y', 'z']:
                        continue
                    plot_data = human.__getattribute__(dimension)
                    # plot
                    data = np.array(plot_data)
                    plt.title(f'{human.trackingId}, {human.gender}, {joint}, {dimension}')
                    plt.plot(data, 'o')
                    plt.show()
                else:
                    dim_order = ['x', 'y', 'z', 'roll', 'pitch', 'yaw']
                    plot_data = human.__getattribute__('joint_' + str(joint))
                    plot_data = [plot_data[i][dim_order.index(dimension)] for i in range(len(plot_data))]
                    # plot
                    data = np.array(plot_data)
                    plt.title(f'{human.trackingId}, {human.gender}, {joint}, {dimension}')
                    plt.plot(data, 'o')
                    plt.show()


# get all target axis
def pick_axis(humans, pattern):
    parameters = pattern.split(',')
    if len(parameters) != 3:
        raise IndexError('wrong pattern.')
    # pick subject
    subjects = []
    if parameters[0] == 'F':
        subjects.append(pick_human(humans, 'gender', 'female'))
    elif parameters[0] == 'M':
        subjects.append(pick_human(humans, 'gender', 'male'))
    elif parameters[0] == 'B':
        subjects.append(pick_human(humans, 'gender', 'female'))
        subjects.append(pick_human(humans, 'gender', 'male'))
    else:
        raise ValueError('wrong pattern of subject picking.')
    # pick joints
    joints = []
    if 'H' in parameters[1]:
        joints.append('H')
        joints.remove('H')
    body_joints = parameters[1].split('J')
    for joint in body_joints:
        if len(joint) != 0:
            joints.append(joint)
    # pick dimensions
    dims = []
    if 'Ro' in parameters[2]:
        dims.append('roll')
    if 'Pi' in parameters[2]:
        dims.append('pitch')
    if 'Ya' in parameters[2]:
        dims.append('yaw')
    if 'X' in parameters[2]:
        dims.append('x')
    # Ya has Y!
    if 'Ya' not in parameters[2] and 'Y' in parameters[2]:
        dims.append('y')
    if 'Z' in parameters[2]:
        dims.append('z')

    return subjects, joints, dims


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


def pick_human(humans, attr, value):
    for human in humans:
        if value == human.__getattribute__(attr):
            return human
    # return untracked human if no matches
    return humans[0]


def main():
    # 0. who am I

    print('>>> WHOAMI:')
    file_name = json_addr.split('\\')[-1][:-5]
    print('Experiment date: 2018.' + file_name[0:2] + '.' + file_name[2:4])
    print('Experiment shift: ' + file_name[4:6])
    print('Experiment session: ' + file_name[6:8])

    # 1. load

    print('>>> LOAD:')
    # separate each object
    # decode error: only one json object each file. one pair of {}.
    print('Loading file...')
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
    print('Frame number: ' + str(frame_num))

    # 2. extract & store

    print('>>> STORE:')
    # start timestamp
    if 'start time' not in json_rawdata[0]:
        raise ValueError('time stamp missing')
    start_time = json_rawdata[0]['start time']
    print('Json file starts at: ' + str(start_time))
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
                print(f'Created human with id: {trackingId}')

            human = pick_human(humans, 'trackingId', trackingId)

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

    if use_plot:
        plot_subjects, plot_joints, plot_dims = pick_axis(humans, plot_pattern)
        # plot
        plot(plot_subjects, plot_joints, plot_dims)

    # 5. time series analyse

    # 5.1 missing value process (interpolation)
    print('>>> INTERPOLATE:')
    for human in humans:
        if human.trackingId == 0:
            continue

        # data missing rate

        # total data count:
        data_count = frame_num * 153  # head 3 + joint 25 * 6
        #print(f'Human ID: {human.trackingId} has total data of: {data_count}')
        # get total missing value count for all axis
        missing_count = 0
        # head
        missing_count += human.roll.count(0)
        missing_count += human.pitch.count(0)
        missing_count += human.yaw.count(0)
        # joints
        for i in range(25):
            joint_data = human.__getattribute__('joint_' + str(i))
            for j in range(6):
                missing_count += [joint_data[n][j] for n in range(len(joint_data))].count(0)
        #print(f'Human ID: {human.trackingId} has Missing Values of: {missing_count}')
        print(f'Human ID: {human.trackingId} \'s missing rate is: {missing_count/data_count}')

    # interpolation (3d spline)
    print('Interpolating...')
    interp_subjects, interp_joints, interp_dims = pick_axis(humans, interp_pattern)
    splines = {}
    for human in interp_subjects:
        for joint in interp_joints:
            for dimension in interp_dims:
                if joint == 'H':
                    if dimension in ['x', 'y', 'z']:
                        continue
                    interp_data = human.__getattribute__(dimension)
                else:
                    dim_order = ['x', 'y', 'z', 'roll', 'pitch', 'yaw']
                    interp_data = human.__getattribute__('joint_' + str(joint))
                    interp_data = [interp_data[i][dim_order.index(dimension)] for i in range(len(interp_data))]
                data = np.array(interp_data)
                # 0 -> np.nan
                np.place(data, data == 0, np.nan)
                # interpolate, see scipy documentation
                x = np.arange(len(data))
                w = np.isnan(data)
                data[w] = 0.
                splines[f'{human.trackingId}&{joint}&{dimension}'] = UnivariateSpline(x, data, w=~w)

                # save as pickle
                with open('data.pickle', 'wb') as f:
                    pickle.dump(data, f)
                with open('spline.pickle', 'wb') as f:
                    pickle.dump(splines[f'{human.trackingId}&{joint}&{dimension}'], f)


if __name__ == '__main__':
    main()
