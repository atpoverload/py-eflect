from easysnmp import Session
from easysnmp.exceptions import EasySNMPTimeoutError

PDU_IP = 'panic-pdu-01.cs.rutgers.edu'
SESSION = None

def sample_pdu():
    global SESSION
    if SESSION is None:
        SESSION = Session(hostname=PDU_IP, community='public', version = 2)

    energy = []
    for outlet_id in (23, 24):
        reading = SESSION.get(['.1.3.6.1.4.1.13742.6.5.4.3.1.4.1.{}.5'.format(outlet_id)])
        energy.append([int(i.value) for i in reading])

    return (time(), tuple(active_powers))

def parse_pdu_data(data):
    parsed_data = []
    for sample in data:
        df = pd.DataFrame(data = zip(sample[1][0], sample[1][1]))
        df /= 1000000
        df.index = ['dram', 'package']
        df.columns.name = 'domain'
        df = df.stack().unstack(0).reset_index()
        df['cpu'] = 0
        df['gpu'] = 0
        df['timestamp'] = pd.to_datetime(sample[0], unit='s')
        parsed_data.append(df)

    return pd.concat(parsed_data).set_index(['timestamp', 'domain'])[['dram', 'cpu', 'package', 'gpu']]
