from datetime import datetime, timedelta
import random


date_start = datetime(2025, 4, 30, 00, 00, 00)
nums_for_telephone_numbers = '01234546789'
call_type = '12'
separator = ', '
counter_records = 0
file_counter = 1
call_start = date_start
date_counter = 1
IterationCount = 100
file = open('InvalidNumbersCDR'+ str(file_counter) + '.csv', 'w')


for i in range(IterationCount):

    call_ends = call_start + timedelta(minutes=random.randint(1, 59)) 
    
    call_middle_midnight = date_start + timedelta(days=date_counter)

    current_type = '0' + ''.join([random.choice(call_type) for x in range(1)]) + separator 
    
    telephone1 = '7' + ''.join([random.choice(nums_for_telephone_numbers) for x in range(11)]) + separator 
    
    telephone2 = '7' + ''.join([random.choice(nums_for_telephone_numbers) for x in range(11)]) + separator 

    if call_start < call_middle_midnight and call_ends > call_middle_midnight and telephone1 != telephone2:
        call_middle_midnight -= timedelta(seconds=1)
        file.write(current_type + telephone1 + telephone2 + call_start.strftime('%Y-%m-%dT%H:%M:%S') + separator + call_middle_midnight.strftime('%Y-%m-%dT%H:%M:%S') + '\n')
        counter_records += 1
        if '01' in current_type:
            current_type = '02' + separator
        else:
            current_type = '01' + separator
        file.write(current_type + telephone2 + telephone1 + call_start.strftime('%Y-%m-%dT%H:%M:%S') + separator + call_middle_midnight.strftime('%Y-%m-%dT%H:%M:%S') + '\n')
        counter_records += 1

        call_middle_midnight += timedelta(seconds=1)
        call_definition= call_ends - call_middle_midnight 
        call_midnight_ends = call_middle_midnight + call_definition
        file.write(current_type + telephone1 + telephone2 + call_middle_midnight.strftime('%Y-%m-%dT%H:%M:%S') + separator + call_midnight_ends.strftime('%Y-%m-%dT%H:%M:%S') + '\n')
        call_start = call_middle_midnight
        counter_records += 1

        if '01' in current_type:
            current_type = '02' + separator
        else:
            current_type = '01' + separator
        file.write(current_type + telephone2 + telephone1 + call_middle_midnight.strftime('%Y-%m-%dT%H:%M:%S') + separator + call_midnight_ends.strftime('%Y-%m-%dT%H:%M:%S') + '\n')
        counter_records += 1

        date_counter += 1
    elif telephone1 != telephone2:
        file.write(current_type + telephone1 + telephone2 + call_start.strftime('%Y-%m-%dT%H:%M:%S') + separator + call_ends.strftime('%Y-%m-%dT%H:%M:%S') + '\n')
        counter_records += 1
        
        if '01' in current_type:
            current_type = '02' + separator
        else:
            current_type = '01' + separator
        file.write(current_type + telephone2 + telephone1 + call_start.strftime('%Y-%m-%dT%H:%M:%S') + separator + call_ends.strftime('%Y-%m-%dT%H:%M:%S') + '\n')
        counter_records += 1

    call_start += timedelta(minutes=random.randint(1, 59))
    if counter_records == 10:
        counter_records = 0
        print('\n' + 'File ' + str(file_counter) + ' consist of 10 records')
        file_counter += 1
        file = open('InvalidNumbersCDR'+ str(file_counter) + '.csv', 'w')