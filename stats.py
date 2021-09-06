import tabula
import pandas as pd
import matplotlib.pyplot as plt
import math

plt.close("all")

# Set your preferences here.
strecke = 'gold'
start_nr = 1097

file = './data/%s.pdf' % (strecke)
stat_info = ['Name', 'Jg', 'Startnr', 'Fahrzeit']

table = tabula.read_pdf(file, pages='all')

df = pd.DataFrame(data=table[0])
for i in range(1, len(table)):
    df = pd.concat([df, table[i]], ignore_index=True)

df = df[df['Name'] != 'Ziel']
num_total = len(df)
print("Anmeldungen %s: %d" % (strecke, num_total))
df = df[df['Fahrzeit'] != 'DNS']
num_starter = len(df)
print("Starter %s: %d" % (strecke, num_starter))
df = df[df['Fahrzeit'] != 'DNF']
num_finisher = len(df)
print("Finisher %s: %d" % (strecke, num_finisher))

last_checkpoint = 'Oberalp'
if last_checkpoint not in df.columns.values:
    last_checkpoint = 'Gotthard'
df = df.dropna(subset=[last_checkpoint])
num_complete = len(df)
print("Vor Kontrollschluss am letzten Checkpoint %s (%s): %d" % (strecke, last_checkpoint, num_complete))

df['Fahrzeit[h]'] = pd.to_timedelta(df['Fahrzeit']).dt.total_seconds() / 3600

df.sort_values(by=['Fahrzeit[h]'], inplace=True)
df.reset_index(inplace=True)
df.index += 1

print('\n')
print('Top 3: ')
print(df.nsmallest(3, 'Fahrzeit[h]')[stat_info])

print('\n')
print('Lantern Rouge: ')
print(df.nlargest(1, 'Fahrzeit[h]')[stat_info])

plt.figure()
plt.title('Alpenbrevet 2021 Fahrzeiten (%s)' % (strecke))

# Approx. every 20 min one bin.
num_bins = int(math.ceil((df['Fahrzeit[h]'].max() - df['Fahrzeit[h]'].min()) * 3))
ax = df['Fahrzeit[h]'].plot.hist(bins=num_bins)
ax.set_xlabel('Fahrzeit [h]')
ax.set_ylabel('Anzahl Finisher')

# Personal stats
yours = df[df['Startnr'] == start_nr]
if len(yours):
    plt.axvline(yours['Fahrzeit[h]'].values[0], color='k', linestyle='dashed', linewidth=1)

    top = math.ceil(len(df[df['Fahrzeit[h]'] <= yours['Fahrzeit[h]'].values[0]]) / num_complete * 100)
    print('\n')
    print('Yours: ')
    print(yours[stat_info])
    print('\nCongratulations, you arrived %d out of %d and in the top %d%% of all finishers that passed the last checkpoint (%s) in time!' % (yours.index[0], num_complete, top, last_checkpoint))

    your_stats = '%s: %s Top: %d%%' % (yours['Name'].values[0], yours['Fahrzeit'].values[0], top)
    plt.text(yours['Fahrzeit[h]'].values[0] + 0.1, 5, your_stats, rotation=90)
else:
    print('\nSorry, did not find your start number %d!' % (start_nr))

plt.savefig('./result/%s.png' % (strecke))
plt.show()
