import subprocess
import argparse
import os
import time

parser = argparse.ArgumentParser()

parser.add_argument('-ne', '--num-experiments', dest="num_experiments", type=int, default=1, help='Number of experiments to run')
parser.add_argument('-p1', '--port1', dest="port1", type=int, default=12121, help='Port 1')
parser.add_argument('-p2', '--port2', dest="port2", type=int, default=34343, help='Port 2')
parser.add_argument('-n', '--noise', dest="noise", type=int, default=1, help='Turn noise on/off')
parser.add_argument('-rs', '--random-seed', dest="rng", type=int, default=0, help='Random Seed')
parser.add_argument('-a1', '--agent-1-location', dest="a1", type=str, default='carrom_agent/start_agent.py', help='relative/full path to agent')
parser.add_argument('-a2', '--agent-2-location', dest="a2", type=str, default='carrom_agent/start_agent.py', help='relative/full path to agent')

args = parser.parse_args()
port1 = args.port1
port2 = args.port2
rng = args.rng
noise = args.noise
a1 = args.a1
a2 = args.a2
ne = args.num_experiments

for i in range(0, args.num_experiments):
    print "Running experiment ", i+1
    try:
        if ne > 1:
            rng = i
        cmd = 'python 1_player_server/start_server.py' + ' -n ' + str(noise) + ' -p1 ' + str(port1) + ' -p2 ' + str(port2) + ' -rs ' + str(rng+100000)
        print cmd
        p1 = subprocess.Popen(cmd.split(' '), shell=False)
        print 'Launched Server'
        time.sleep(2)
        cmd1 = 'python ' + a1 + ' -p ' + str(port1) + ' -rs ' + str(rng+50000) + ' -n 1'
        print cmd1
        p2 = subprocess.Popen(cmd1.split(' '), shell=False)
        print 'Launched Player 1 Agent'
        time.sleep(2)
        cmd2 = 'python ' + a2 + ' -p ' + str(port2) + ' -rs ' + str(rng+250000) + ' -n 2'
        print cmd2
        p3 = subprocess.Popen(cmd2.split(' '), shell=False)
        print 'Launched Player 2 Agent'
        p1.communicate()
    except Exception as e:
        print "Error: ", e
    finally:
        try:
            p1.terminate()
            p1.kill()
        except:
            pass
        try:
            p2.terminate()
            p2.kill()
            time.sleep(1)
        except:
            pass
        try:
            p3.terminate()
            p3.kill()
            time.sleep(1)
        except:
            pass
