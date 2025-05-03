from datetime import datetime, timedelta
import random


date_start = datetime(2025, 4, 30, 00, 00, 00)
call_type = '12'
separator = ', '
counter_records = 0
file_counter = 1
call_start = date_start
date_counter = 1
IterationCount = 100

fixed_numbers = [
    '79991113355','79992224466','79993335577','79994446688','79995557799',
    '79996668800','79997779911','79998880022','79990001133','79991112244',
    '79992223355','79993334466','79994445577','79995556688','79906667799',
    '79907778800','79908889911','79909990022','79900001144','79901113366',
    '79902224477','79903335588','79904446699','79905557700','79906668811',
    '79907779922','79908880033','79909991144'
]
file = open('LessrecordsCDR'+ str(file_counter) + '.csv', 'w')


for i in range(IterationCount):

    call_ends = call_start + timedelta(minutes=random.randint(1, 59)) 
    
    call_middle_midnight = date_start + timedelta(days=date_counter)

    current_type = '0' + ''.join([random.choice(call_type) for x in range(1)]) + separator 
    
    telephone1, telephone2 = random.sample(fixed_numbers, 2)
    telephone1 += separator
    telephone2 += separator
    
    if call_start < call_middle_midnight and call_ends > call_middle_midnight and telephone1 != telephone2:
        call_middle_midnight -= timedelta(seconds=1)
        
    
        file.write(current_type + telephone1 + telephone2 + call_start.strftime('%Y-%m-%dT%H:%M:%S') + separator + call_middle_midnight.strftime('%Y-%m-%dT%H:%M:%S') + '\n')
        counter_records += random.randint(1, 2)
        

        if '01' in current_type:
            current_type = '02' + separator
        else:
            current_type = '01' + separator


        file.write(current_type + telephone2 + telephone1 + call_start.strftime('%Y-%m-%dT%H:%M:%S') + separator + call_middle_midnight.strftime('%Y-%m-%dT%H:%M:%S') + '\n')
        counter_records += random.randint(1, 2)


        call_middle_midnight += timedelta(seconds=1)
        call_definition = call_ends - call_middle_midnight 
        call_midnight_ends = call_middle_midnight + call_definition 


        file.write(current_type + telephone1 + telephone2 + call_start.strftime('%Y-%m-%dT%H:%M:%S') + separator + call_midnight_ends.strftime('%Y-%m-%dT%H:%M:%S') + '\n')
        counter_records += random.randint(1, 2)
        

        call_start = call_middle_midnight
        if '01' in current_type:
            current_type = '02' + separator
        else:
            current_type = '01' + separator


        file.write(current_type + telephone2 + telephone1 + call_start.strftime('%Y-%m-%dT%H:%M:%S') + separator + call_midnight_ends.strftime('%Y-%m-%dT%H:%M:%S') + '\n')
        counter_records += random.randint(1, 2)


        date_counter += 1
    elif telephone1 != telephone2:
        
        file.write(current_type + telephone1 + telephone2 + call_start.strftime('%Y-%m-%dT%H:%M:%S') + separator + call_ends.strftime('%Y-%m-%dT%H:%M:%S') + '\n')
        counter_records += random.randint(1, 2)


        if '01' in current_type:
            current_type = '02' + separator
        else:
            current_type = '01' + separator
        
        file.write(current_type + telephone1 + telephone2 + call_start.strftime('%Y-%m-%dT%H:%M:%S') + separator + call_ends.strftime('%Y-%m-%dT%H:%M:%S') + '\n')
        counter_records += random.randint(1, 2)

    call_start += timedelta(minutes=random.randint(1, 59))
    if counter_records >= 9:
        counter_records = 0
        file_counter += 1
        file = open('LessrecordsCDR'+ str(file_counter) + '.csv', 'w')