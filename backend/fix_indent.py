with open('insider_threat_system/email_ingestor.py', 'r') as f:
    lines = f.readlines()

for i in range(94, 255):
    if lines[i].startswith('            '):
        lines[i] = lines[i][4:]

with open('insider_threat_system/email_ingestor.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
