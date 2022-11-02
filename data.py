from collections import defaultdict
import os
import pandas as pd

send_list=[]
temp = []
consensus_temp = []
name_temp = []
node_list = []
round_list = []
tx_list = []
delay_list = []
batch_list = []
id_list = []



def to_send_old(client_path, send_list,r):
    # r = 2
    count = {}
    count1 = 0
    count2 = 0
    client = open(client_path, 'r', encoding='utf-8')
    lines_client = client.readlines()
    if len(lines_client) == 0:
        for i in range(r):
            send_list.append(0)
    for line in lines_client:
        for i in range(r):
            if '_handle_send_loop' in line and ('('+str(i)+',') in line:
                # print('running')
                count[i] = count.get(i, 0) + 1
                # count[i] = count[i] + 1
        # if '_handle_send_loop' in line and '(0,' in line:
        #     count1+=1
        # if '_handle_send_loop' in line and '(1,' in line:
        #     count2+=1
    # count = count / 2
    for i in range(r):
        send_list.append(count.get(i, 0))
    # send_list.append(count1)
    # send_list.append(count2)
    # print('this is the count',count, count.items())
    print(count)
    

def to_send(client_path, send_list, r):
    # r = 2 
    count = 0
    client = open(client_path, 'r', encoding='utf-8')
    lines_client = client.readlines()
    for l in lines_client:
        if 'this is the send account' in l:
            count+=1
    # send_line = (lines_client[len(lines_client)-1])
    # print(send_line.split(), client_path)
    # count = int(send_line.split()[11]) / 2
    for _ in range(r):
        send_list.append(count)

def send_count(client_path, send_list, r, omit):
    count1 = 0
    count2 = 0
    # count = defaultdict(set) 
    count = {}
    client = open(client_path, 'r', encoding='utf-8')
    lines_client = client.readlines()
    if len(lines_client) == 0:
        for i in range(r):
            send_list.append(0)
    for line in lines_client:
        for i in range(r):
            if '_handle_send_loop' in line and ('round '+str(i)) in line:
                if omit == 0:
                    count[i] = count.get(i, 0) + 1
                else:
                    count[i] = count.get(i, 0) + 10
        # if '_handle_send_loop' in line and '(0,' in line:
        #     count1+=1
        # if '_handle_send_loop' in line and '(1,' in line:
        #     count2+=1
    for i in range(r):
        send_list.append(count.get(i, 0))
    # send_list.append(count1)
    # send_list.append(count2)

def dumbo_data(consensus_path, node_list, delay_list, tx_list, round_list, batch_list, id_list, r):
    # r = 2
    acon = 0
    tcon = 0
    consensus = open(consensus_path, 'r', encoding='utf-8')
    node = consensus_path.split('-')[0][10:]
    batchsize = consensus_path.split('-')[2]
    jid = consensus_path.split('-')[5][:-4]
    for _ in range(r):
        id_list.append(jid)
        node_list.append(node)
        batch_list.append(batchsize)
    lines = consensus.readlines()
    if len(lines) == 0:
        delay = 'null'
        tx = 'null'
        round = 'null'
        for _ in range(r):
            delay_list.append(delay)
            tx_list.append(tx)
            round_list.append(round)
    for l in lines:
        if 'ACS Block delay' in l and acon < r:
            delay = l.split()[12]
            delay_list.append(delay)
            acon+=1
        elif 'Delivers ACS Block' in l and tcon < r:
            round = l.split()[13]
            tx = l.split()[16]
            tx_list.append(tx)
            round_list.append(round)
            tcon +=1

def hbbft_data(consensus_path, node_list, delay_list, tx_list, round_list, batch_list, id_list, r):
    acon = 0
    tcon = 0
    consensus = open(consensus_path, 'r', encoding='utf-8')
    node = consensus_path.split('-')[0][10:]
    # node = consensus_path.split('-')[0][6:]
    batchsize = consensus_path.split('-')[2]
    jid = consensus_path.split('-')[5][:-4]
    for _ in range(r):
        id_list.append(jid)
        node_list.append(node)
        batch_list.append(batchsize)
    line = consensus.readlines()
    if len(line) == 0 or len(line) < 3:
        delay = 'null'
        tx = 'null'
        round = 'null'
        for _ in range(r):
            delay_list.append(delay)
            tx_list.append(tx)
            round_list.append(round)
    for l in line:
        if 'ACS Block Delay' in l and acon < r:
            delay = l.split()[-1]
            delay_list.append(delay)
            acon+=1
        if 'Delivers ACS Block' in l and tcon < r:
            round = l.split()[-5]
            tx = l.split()[-2]
            tx_list.append(tx)
            round_list.append(round)
            tcon +=1

def bdt_data(consensus_path, node_list, delay_list, tx_list, round_list, batch_list, id_list, r):
    acon = 0
    tcon = 0
    consensus = open(consensus_path, 'r', encoding='utf-8')
    node = consensus_path.split('-')[0][8:]
    batchsize = consensus_path.split('-')[2]
    jid = consensus_path.split('-')[5][:-4]
    for _ in range(r):
        id_list.append(jid)
        node_list.append(node)
        batch_list.append(batchsize)
    line = consensus.readlines()
    if len(line) == 0:
        delay = 'null'
        tx = 'null'
        round = 'null'
        for _ in range(r):
            delay_list.append(delay)
            tx_list.append(tx)
            round_list.append(round)
    temp_delay = 0
    temp_tx = 0
    for l in line:
        if 'with total delivered Txs' in l:
            # print(l.split())
            delay = float(l.split()[10])
            if (temp_delay != delay):
                delay = delay - temp_delay
                delay_list.append(delay)
                temp_delay = delay
            round = l.split()[14]
            round_list.append(round)
            tx = int(l.split()[19])
            if(tx == 0):
                tx_list.append(tx)
            if (temp_tx != tx):
                tx = tx - temp_tx
                tx_list.append(tx)
                temp_tx = tx
    if len(delay_list) % r != 0:
        delay_list.append(0)
        tx_list.append(0)
        round_list.append(1)
    print(consensus_path, len(id_list), len(round_list), len(tx_list), len(delay_list), len(batch_list))

def hbbft_shard_data(consensus_path, node_list, delay_list, tx_list, round_list, batch_list, id_list, r):
    acon = 0
    tcon = 0
    consensus = open(consensus_path, 'r', encoding='utf-8')
    node = consensus_path.split('-')[0][20:]
    batchsize = consensus_path.split('-')[2]
    jid = consensus_path.split('-')[5][:-4]
    for _ in range(r):
        id_list.append(jid)
        node_list.append(node)
        batch_list.append(batchsize)
    line = consensus.readlines()
    if len(line) == 0:
        delay = 'null'
        tx = 'null'
        round = 'null'
        for _ in range(r):
            delay_list.append(delay)
            tx_list.append(tx)
            round_list.append(round)
    for l in line:
        if 'ACS Block Delay' in l and acon < r:
            delay = l.split()[-1]
            delay_list.append(delay)
            acon+=1
        if 'Delivers ACS Block' in l and tcon < r:
            round = l.split()[-5]
            tx = l.split()[-2]
            tx_list.append(tx)
            round_list.append(round)
            tcon +=1
    if len(delay_list) % r != 0:
        delay_list.append(0)
        tx_list.append(0)
        round_list.append(1)


def file_deal(path,protocol, round, L):
    path = path + '/' + protocol
    f = os.listdir(path)
    f.sort(key=lambda x:(int(x.split('-')[0]), int(x.split('-')[2])))
    for mkdir in f:
        name = os.listdir(path + '/' + mkdir)
        for i in name:
            if 'client' in i:
                client = path + '/' + mkdir+'/'+i
                temp.append(client)    
    for file in temp:
        # to_send_old(file, send_list)
        id = (file.split('-')[6][:-4])
        omit = int(id) % L
        send_count(file, send_list, round, omit)

    for mkdir in f:
        name = os.listdir(path + '/' + mkdir)
        for i in name:
            if 'consensus' in i:
                consensus = path + '/' + mkdir+'/'+i
                consensus_temp.append(consensus)

    for file in consensus_temp:
        if protocol == 'dumbo':
            dumbo_data(file,node_list, delay_list, tx_list, round_list, batch_list, id_list, round)
        elif protocol == 'hbbft':
            hbbft_data(file,node_list, delay_list, tx_list, round_list, batch_list, id_list, round)
        elif protocol == 'hbbft_shard_new':
            hbbft_shard_data(file,node_list, delay_list, tx_list, round_list, batch_list, id_list, round)
        elif protocol == 'bdt':
            bdt_data(file,node_list, delay_list, tx_list, round_list, batch_list, id_list, round)


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--P', metavar='P', required=True,
                        help='protocol', type=str)
    parser.add_argument('--FP', metavar='FP', required=False,
                        help='data contents', type=str, default='log')
    parser.add_argument('--K', metavar='K', required=True,
                        help='rounds to execute', type=int)
    parser.add_argument('--L', metavar='L', required=False,
                        help='amount of all record logger', type=int, default=12)
    args = parser.parse_args()

    P = args.P
    K = args.K
    FP = args.FP
    L = args.L


    # if P == 'dumbo':
    #     file_deal(FP+'dumbo', K, L)
    # elif P == 'hbbft':
    #     file_deal(FP+'hbbft', K, L)
    # elif P == 'hbbft_shard':
    #     file_deal(FP+'hbbft_shard_new', K, L)
    # elif P == 'bdt':
    #     file_deal(FP+'bdt', K, L)
    if P == 'dumbo':
        file_deal(FP,'dumbo', K, L)
    elif P == 'hbbft':
        file_deal(FP,'hbbft', K, L)
    elif P == 'hbbft_shard':
        file_deal(FP,'hbbft_shard_new', K, L)
    elif P == 'bdt':
        file_deal(FP,'bdt', K, L)

    dict = {'id': id_list, 'node':node_list, 'batchsize':batch_list, 'delay':delay_list,'tx':tx_list, 'send':send_list, 'round': round_list}
    print(dict)
    df = pd.DataFrame(dict)
    # df.to_csv('dumbo_test.csv', index=False,)
    df.to_csv(P + '.csv', index=False)

    print('数据处理完成')
    # print(df)