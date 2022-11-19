import pandas as pd

mean_shard = []
tx_list = []
send_list = []
r = 7
node_list = [32, 48, 64, 80, 96]
# node_list = [16,32,64,96]
# shard_set = {16:4,32:8, 64:8, 96:12}
shard_set = {32:2,48:3, 64:4, 80:5, 96:6}
batchsize_list = [1000, 2000, 3000, 4000, 5000]
per_list = [0.1, 0.2, 0.3, 0.4, 0.5]

def data_work(protocol):
    if protocol == 'hbbft_shard':
        print('The protocol:',str(protocol),'node_list:',node_list,'batchsize_list', batchsize_list, 'shard_list:',shard_set)
    elif protocol == 'hbbft_shard_arbc':
        print('The protocol:',str(protocol),'node_list:',node_list,'batchsize_list', batchsize_list, 'shard_list:',shard_set,'per_list:',per_list)
    else:
        print('The protocol:',str(protocol),'node_list:',node_list,'batchsize_list', batchsize_list)
    # path = str(protocol)+'.csv'
    path = 'hbbft_shard_3.csv'
    df = pd.read_csv(path)
    for node in node_list:
        shard = int(shard_set[node])  #分片的组数
        for batchsize in batchsize_list:
            mean_shard.clear()
            tx_list.clear()
            send_list.clear()
            total_delay = 0
            total_tx = 0
            total_send = 0
            ttx = 0
            mean_tx = 0
            for i in range(node):
                if protocol == 'dumbo':
                    data = (df.loc[(df['id'] == i) & (df['node'] == node) & (df['batchsize'] == batchsize * node),:])
                elif protocol == 'hbbft_shard':
                    data = (df.loc[(df['id'] == i) & (df['node'] == node) & (df['batchsize'] == batchsize) & (df['shard'] == shard),:])
                    # print(data)
                else:
                    data = (df.loc[(df['id'] == i) & (df['node'] == node) & (df['batchsize'] == batchsize),:])
                delay = (data['delay'].astype('float').sum()) / r
                tx =(data['tx'].astype('float').sum()) / r
                send = (data['send'].astype('float').sum()) / r
                if tx != 0:
                    # print('this is the node tx', i, tx)
                    tx_list.append(tx)
                if protocol == 'hbbft':
                    if node >= 48:
                        if send > 20000:
                            send_list.append(send)
                    else:
                        if send > 200:
                            send_list.append(send)
                else:
                    if send > 200: #发送量注意判断条件
                        send_list.append(send)
                if delay != 0:
                    mean_shard.append(delay)
            for i in range(len(mean_shard)):
                total_delay += mean_shard[i]
            mean_delay = total_delay / len(mean_shard)
            for i in range(len(send_list)):
                total_send += send_list[i]
            for i in range(len(tx_list)):
                ttx += tx_list[i]
            if (protocol == 'hbbft_shard'):
                total_tx = ttx/len(tx_list) * shard
            else:
                total_tx = ttx/len(tx_list)
            mean_tps = (total_tx / mean_delay)
            mean_tx = total_tx / shard
            mean_send = total_send / len(send_list)
            if(protocol == 'hbbft_shard'):
                print('node:',node,'batchsize:', batchsize, 'shard_number:', shard,'mean_delay:', mean_delay,'total tx:', total_tx,'mean_tx:',mean_tx, 'mean_tps:', mean_tps,'mean_send:', mean_send)
            else:
                print('node:',node,'batchsize:',batchsize,'mean_delay:', mean_delay,'total tx:', total_tx,'mean_tx:',total_tx, 'mean_tps:', mean_tps,'mean_send:', mean_send)
            
        print('')   

def data_work_arbc(protocol):
    shard_set = {32:4,48:6, 64:8, 80:10, 96:12}
    if protocol == 'hbbft_shard':
        print('The protocol:',str(protocol),'node_list:',node_list,'batchsize_list', batchsize_list, 'shard_list:',shard_set)
    elif protocol == 'hbbft_shard_arbc':
        print('The protocol:',str(protocol),'node_list:',node_list,'batchsize_list', batchsize_list, 'shard_list:',shard_set,'per_list:',per_list)
    else:
        print('The protocol:',str(protocol),'node_list:',node_list,'batchsize_list', batchsize_list)
    path = str(protocol)+'.csv'
    
    df = pd.read_csv(path)
    for node in node_list:
        shard = shard_set[node]  #分片的组数
        for batchsize in batchsize_list:
            for per in per_list:
                # print(per)
                mean_shard.clear()
                tx_list.clear()
                send_list.clear()
                total_delay = 0
                total_tx = 0
                total_send = 0
                ttx = 0
                mean_tx = 0
                for i in range(node):
                    data = (df.loc[(df['id'] == i) & (df['node'] == node) & (df['batchsize'] == batchsize) & (df['per'] == per),:])
                    delay = (data['delay'].astype('float').sum()) / r
                    tx =(data['tx'].astype('float').sum()) / r
                    send = (data['send'].astype('float').sum()) / r
                    # per = (data['per'].astype('float').sum()) / r
                    if tx != 0:
                        # print('this is the node tx', i, tx)
                        tx_list.append(tx)
                    # if protocol == 'hbbft':
                    if node == 48:
                        # print(send)
                        if send > 5000:
                            send_list.append(send)
                    elif node == 80:
                        if send > 6000:
                            send_list.append(send)
                    elif node == 64:
                        if send > 5000:
                            send_list.append(send)
                    elif node == 96:
                        if per <= 0.1:
                            if send > 5000:
                                send_list.append(send)
                        else:
                            if send > 5000:
                                send_list.append(send)
                    else:
                        if send > 2000:
                            send_list.append(send)
                    # else:
                    #     if send > 200: #发送量注意判断条件
                    #         send_list.append(send)
                    if delay != 0:
                        mean_shard.append(delay)
                for i in range(len(mean_shard)):
                    total_delay += mean_shard[i]
                mean_delay = total_delay / len(mean_shard)
                for i in range(len(send_list)):
                    total_send += send_list[i]
                for i in range(len(tx_list)):
                    ttx += tx_list[i]
                total_tx = ttx/len(tx_list) * shard
                mean_tps = (total_tx / mean_delay)
                mean_tx = total_tx / shard
                # print(len(send_list))
                mean_send = total_send / len(send_list)
                print('node:',node,'batchsize:', batchsize, 'shard_number:', shard,'mean_delay:',mean_delay, 'per:', per,'total tx:', total_tx,'mean_tx:',mean_tx, 'mean_tps:', mean_tps,'mean_send:', mean_send)
            print('') 
        print('')  



if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--P', metavar='P', required=False,default='',
                        help='protocol', type=str)
    args = parser.parse_args()

    P = args.P

    protocols = ['hbbft', 'dumbo', 'hbbft_shard']

    if P == '':
        for protocol in protocols:
            data_work(protocol)
    elif P == 'hbbft_shard_arbc':
        data_work_arbc(P)
    else:
        data_work(protocol=P)
