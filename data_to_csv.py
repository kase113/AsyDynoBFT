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
shard_list = []
total_tx_list = []
id_list = []
shard_id_list = []
arbc_list = []
per_list = []



def to_send_old(client_path, send_list,r):
    # r = 2
    count = {}
    client = open(client_path, 'r', encoding='utf-8')
    lines_client = client.readlines()
    if len(lines_client) == 0:
        for i in range(r):
            send_list.append(0)
    for line in lines_client:
        for i in range(r):
            if '_handle_send_loop' in line and ('('+str(i)+',') in line:
                count[i] = count.get(i, 0) + 1
    for i in range(r):
        send_list.append(count.get(i, 0))
    # print(count)
    

def to_send(client_path, send_list, r):
    # r = 2 
    count = 0
    client = open(client_path, 'r', encoding='utf-8')
    lines_client = client.readlines()
    for l in lines_client:
        if 'this is the send account' in l:
            count+=1
    for _ in range(r):
        send_list.append(count)

def send_count(client_path, send_list, r, omit):
    count1 = 0
    count2 = 0
    # count = defaultdict(set) 
    # print('running send count')
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
    for i in range(r):
        send_list.append(count.get(i, 0))

def dumbo_data(consensus_path, node_list, delay_list, tx_list, round_list, batch_list, id_list, r):
    # r = 2
    acon = 0
    tcon = 0
    consensus = open(consensus_path, 'r', encoding='utf-8')
    path_len=len(consensus_path.split('-'))
    node = consensus_path.split('-')[0].split('/')[-1]
    batchsize = consensus_path.split('-')[2]
    jid = consensus_path.split('-')[path_len-1][:-4]
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
    path_len=len(consensus_path.split('-'))
    node = consensus_path.split('-')[0].split('/')[-1]
    batchsize = consensus_path.split('-')[2]
    jid = consensus_path.split('-')[path_len-1][:-4]
    for _ in range(r):
        id_list.append(jid)
        node_list.append(node)
        batch_list.append(batchsize)
    line = consensus.readlines()
    if len(line) == 0 or len(line) < 3:
        delay = 0
        tx = 0
        round = 'null'
        for _ in range(r):
            delay_list.append(delay)
            tx_list.append(tx)
            round_list.append(round)
    for l in line:
        if 'ACS Block Delay' in l and acon < r:
            delay = float(l.split()[-1])
            delay_list.append(delay)
            acon+=1
        if 'Delivers ACS Block' in l and tcon < r:
            round = l.split()[-5]
            tx = int(l.split()[-2])
            tx_list.append(tx)
            round_list.append(round)
            tcon +=1

def bdt_data(consensus_path, node_list, delay_list, tx_list, round_list, batch_list, id_list, r):
    acon = 0
    tcon = 0
    consensus = open(consensus_path, 'r', encoding='utf-8')
    path_len=len(consensus_path.split('-'))
    node = consensus_path.split('-')[0].split('/')[-1]
    batchsize = consensus_path.split('-')[2]
    jid = consensus_path.split('-')[path_len-1][:-4]
    for _ in range(r):
        id_list.append(jid)
        node_list.append(node)
        batch_list.append(batchsize)
    line = consensus.readlines()
    if len(line) <= 100 :
        delay = '0'
        tx = '0'
        round = '0'
        for _ in range(r):
            delay_list.append(delay)
            tx_list.append(tx)
            round_list.append(round)
    temp_delay = 0
    temp_tx = 0
    for l in line:
        if 'with total delivered Txs' in l and acon < r:
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
            acon+=1
            # print('this is the acon', acon)

    if len(delay_list) % r != 0:
        # print('queshi')
        delay_list.append(0)
        tx_list.append(0)
        round_list.append(1)
    print(consensus_path, len(id_list), len(round_list), len(tx_list), len(delay_list), len(batch_list), len(send_list))

def hbbft_shard_data(consensus_path, node_list, delay_list, tx_list, round_list, batch_list, id_list, shard_id_list, shard_list,total_tx_list,arbc_list, r, arbc):
    acon = 0
    tcon = 0
    scon = 0
    arbc_count = {}
    consensus = open(consensus_path, 'r', encoding='utf-8')
    path_len=len(consensus_path.split('-'))
    shard = int(consensus_path.split('-')[4])
    node = consensus_path.split('-')[0].split('/')[-1]
    batchsize = consensus_path.split('-')[2]
    jid = consensus_path.split('-')[path_len-1][:-4]
    for _ in range(r):
        id_list.append(jid)
        node_list.append(node)
        batch_list.append(batchsize)
        shard_list.append(shard)
    temp_tx = 0
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
        if arbc == True:
            for i in range(r):
                if 'in round of ' + str(i) in line:
                    arbc_count[i] = arbc_count.get(i, 0) + 1
        if 'ACS Block Delay' in l and acon < r:
            delay = l.split()[-1]
            delay_list.append(delay)
            acon+=1
        if 'Delivers ACS Block' in l and tcon < r:
            round = l.split()[-5]
            round_list.append(round)
            tx = int(l.split()[-2])
            if tx != temp_tx:
                temp = tx
                tx = tx - temp_tx
                tx_list.append(tx)
                temp_tx = temp
            tcon +=1
            total_tx = tx * shard
            total_tx_list.append(total_tx)
        if 'seconds with total delivered Txs' in l and scon < r:
            shard_id = int((l.split()[10]))
            shard_id_list.append(shard_id)
            scon+=1
    if len(delay_list) % r != 0:
        delay_list.append(0)
        tx_list.append(0)
        round_list.append(1)
    if tcon < r:
        for _ in range(tcon, r):
            total_tx_list.append(0)
    if len(shard_id_list) % r != 0:
        shard_id_list.append(0)
    # for i in range(r):
    #     arbc_list.append(arbc_count.get(i, 0))
    # print(consensus_path, len(id_list), len(round_list), len(tx_list), len(delay_list), len(batch_list), len(send_list))
    # print(consensus_path, len(total_tx_list),len(delay_list))

def hbbft_shard_arbc_data(consensus_path, node_list, delay_list, tx_list, round_list, batch_list, id_list, shard_id_list, shard_list,total_tx_list,arbc_list, per_list, r, arbc):
    acon = 0
    tcon = 0
    scon = 0
    arbc_count = {}
    consensus = open(consensus_path, 'r', encoding='utf-8')
    # print(consensus_path)
    
    path_len=len(consensus_path.split('-'))
    shard = int(consensus_path.split('-')[4])
    per = float(consensus_path.split('/')[-2].split('-')[-1])
    node = consensus_path.split('-')[0].split('/')[-1]
    batchsize = consensus_path.split('-')[2]
    jid = consensus_path.split('-')[path_len-1][:-4]
    for _ in range(r):
        id_list.append(jid)
        node_list.append(node)
        batch_list.append(batchsize)
        shard_list.append(shard)
        per_list.append(per)
    temp_tx = 0
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
        # if arbc == True:
        #     for i in range(r):
        #         if 'in round of ' + str(i) in line:
        #             arbc_count[i] = arbc_count.get(i, 0) + 1
        if 'ACS Block Delay' in l and acon < r:
            delay = l.split()[-1]
            delay_list.append(delay)
            acon+=1
        if 'Delivers ACS Block' in l and tcon < r:
            round = l.split()[-5]
            round_list.append(round)
            tx = int(l.split()[-2])
            if tx != temp_tx:
                temp = tx
                tx = tx - temp_tx
                tx_list.append(tx)
                temp_tx = temp
            tcon +=1
            total_tx = tx * shard
            total_tx_list.append(total_tx)
        if 'seconds with total delivered Txs' in l and scon < r:
            shard_id = int((l.split()[10]))
            shard_id_list.append(shard_id)
            scon+=1
    if len(delay_list) % r != 0:
        delay_list.append(0)
        tx_list.append(0)
        round_list.append(1)
    if tcon < r:
        for _ in range(tcon, r):
            total_tx_list.append(0)
    if len(shard_id_list) % r != 0:
        shard_id_list.append(0)
    # for i in range(r):
    #     arbc_list.append(arbc_count.get(i, 0))
    # print(consensus_path, len(id_list), len(round_list), len(tx_list), len(delay_list), len(batch_list), len(send_list))
    # print(consensus_path, len(total_tx_list),len(delay_list))


def file_deal(path,protocol, round, L, arbc):
    path = path + '/' + protocol 
    # path = path + '/' + 'hbbft_shard_new' + '/per'
    # print(path)
    f = os.listdir(path)
    f.sort(key=lambda x:(int(x.split('-')[0]), int(x.split('-')[2])))
    for mkdir in f:
        # if keyN == mkdir.split('-')[0]:
            name = os.listdir(path + '/' + mkdir)
            # print(name)
            for i in name:
                if 'client' in i:
                    client = path + '/' + mkdir+'/'+i
                    temp.append(client)    
    # print(temp)
    for file in temp:
        # to_send_old(file, send_list)
        name_id = (file.split('-'))
        # print(name_id)
        id = (file.split('-')[len(name_id)-1][:-4])
        # print(id)
        omit = int(id) % L
        send_count(file, send_list, round, omit)

    for mkdir in f:
        # if keyN == mkdir.split('-')[0]:
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
        elif protocol == 'hbbft_shard':
            hbbft_shard_data(file, node_list, delay_list, tx_list, round_list, batch_list, id_list, shard_id_list, shard_list,total_tx_list, arbc_list, round, arbc)
        elif protocol == 'hbbft_shard_arbc':
            # print('protocol is running')
            hbbft_shard_arbc_data(file,node_list, delay_list, tx_list, round_list, batch_list, id_list, shard_id_list, shard_list,total_tx_list, arbc_list, per_list, round, arbc)
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
    parser.add_argument('--S', metavar='S', required=False,
                        help='data csv name', type=str, default='new_data')
    parser.add_argument('--T', metavar='T', required=False,
                        help='flag of arbc', type=bool, default=False)

    args = parser.parse_args()

    P = args.P
    K = args.K
    FP = args.FP
    L = args.L
    save_file_name = args.S
    arbc = args.T

    if P == 'dumbo':
        file_deal(FP,'dumbo', K, L, arbc)
    elif P == 'hbbft':
        file_deal(FP,'hbbft', K, L, arbc)
    elif P == 'hbbft_shard':
        file_deal(FP,'hbbft_shard', K, L, arbc)
    elif P == 'hbbft_shard_arbc':
        file_deal(FP,'hbbft_shard_arbc', K, L, arbc)
    elif P == 'bdt':
        file_deal(FP,'bdt', K, L, arbc)


    tps_list = []
    total_tps_list = []
    if P == 'hbbft_shard':
        print(len(id_list),len(node_list), len(shard_list), len(batch_list), len(delay_list), len(tx_list), len(total_tx_list), len(send_list),len(round_list))
        dict = {'id': id_list, 'node':node_list, 'shard':shard_list, 'batchsize':batch_list, 'delay':delay_list, 'tx':tx_list, 'total_tx':total_tx_list, 'send':send_list, 'round': round_list}
    elif P == 'hbbft_shard_arbc':
        print(len(id_list),len(shard_id_list), len(node_list), len(shard_list), len(per_list), len(batch_list), len(delay_list), len(tx_list), len(total_tx_list), len(send_list),len(round_list))
        dict = {'id': id_list, 'shard_id': shard_id_list, 'node':node_list, 'shard':shard_list, 'per':per_list, 'batchsize':batch_list, 'delay':delay_list, 'tx':tx_list, 'total_tx':total_tx_list, 'send':send_list, 'round': round_list}
    else:
        dict = {'id': id_list, 'node':node_list, 'batchsize':batch_list, 'delay':delay_list,'tx':tx_list, 'send':send_list, 'round': round_list}
    # print(dict)
    df = pd.DataFrame(dict)
    
    if P == 'hbbft_shard':
        for i in df.index:
            if float(df['tx'].at[i]) == 0 or float(df['delay'].at[i]) == 0:
                tps = 0
            else:
                tps= float(df['tx'].at[i]) / float(df['delay'].at[i])
            tps_list.append(tps)
            total_tps = tps * float(df['shard'].at[i])
            total_tps_list.append(total_tps)
        # print(len(id_list),len(shard_id_list), len(node_list), len(shard_list), len(batch_list), len(delay_list), len(tx_list),len(tps_list), len(total_tx_list), len(total_tx_list), len(send_list),len(round_list))
        dict = {'id': id_list, 'shard_id': shard_id_list, 'node':node_list, 'shard':shard_list, 'batchsize':batch_list, 'delay':delay_list, 'tx':tx_list,'tps':tps_list, 'total_tx':total_tx_list, 'total_tps':total_tps_list, 'send':send_list, 'round': round_list}
    elif P == 'hbbft_shard_arbc':
        for i in df.index:
            if float(df['tx'].at[i]) == 0 or float(df['delay'].at[i]) == 0:
                tps = 0
            else:
                tps= float(df['tx'].at[i]) / float(df['delay'].at[i])
            tps_list.append(tps)
            total_tps = tps * float(df['shard'].at[i])
            total_tps_list.append(total_tps)
        # print(len(id_list),len(shard_id_list), len(node_list), len(shard_list), len(batch_list), len(delay_list), len(tx_list),len(tps_list), len(total_tx_list), len(total_tx_list), len(send_list),len(round_list))
        dict = {'id': id_list, 'shard_id': shard_id_list, 'node':node_list, 'shard':shard_list, 'per':per_list, 'batchsize':batch_list, 'delay':delay_list, 'tx':tx_list,'tps':tps_list, 'total_tx':total_tx_list, 'total_tps':total_tps_list, 'send':send_list, 'round': round_list}
    else:
        for i in df.index:
            if float(df['tx'].at[i]) == 0 or float(df['delay'].at[i]) == 0:
                tps = 0
            else:
                tps= float(df['tx'].at[i]) / float(df['delay'].at[i])
            tps_list.append(tps)
        dict = {'id': id_list, 'node':node_list, 'batchsize':batch_list, 'delay':delay_list,'tx':tx_list, 'tps': tps_list, 'send':send_list, 'round': round_list}
    df = pd.DataFrame(dict)
    print(df)
    df.to_csv(save_file_name + '.csv', index=False)

    print('数据提取csv完成')
