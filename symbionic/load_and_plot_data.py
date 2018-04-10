'''
currently just a script
@author: Matthijs Cox
'''

import symbionic

folder = r"C:\Users\matcox\TMC\Teamsite - Documenten\Data\OYMotion-sample\data"
folder = folder.replace("\\", "/")

emg_data = symbionic.EmgData()
emg_data.load_training_data(folder + '/g1/535-170309-g1-20-f1.hex', gesture='g1')
emg_data.load_training_data(folder + '/g2/226-170310-g2-20-f2.hex', gesture='g2')
emg_data.load_training_data(folder + '/g3/226-170310-g3-20-f2.hex', gesture='g3')
emg_data.load_training_data(folder + '/g4/226-170310-g4-20-f2.hex', gesture='g4')
emg_data.load_training_data(folder + '/g5/533-170309-g5-20-f1.hex', gesture='g5')
emg_data.load_training_data(folder + '/g6/226-170310-g6-20-f2.hex', gesture='g6')
emg_data.label_patterns()

fig = symbionic.plot(emg_data)