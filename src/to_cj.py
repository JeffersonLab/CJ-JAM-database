## convert the excel file to CJ fitpack format (plain text), include correlated errors(in %)
## usage: to_cj.py [exp_id]
##       input: exp_id
##       output: converted file under {pwd}/to_cj_output/
import pandas as pd
import numpy as np
import sys
import os

exp_id = sys.argv[1]

file_path = f"../data/dataframe/{exp_id}.xlsx"
try:
    xls = pd.ExcelFile(file_path)
    format_sheets = [sheet for sheet in xls.sheet_names if "format" in sheet.lower()]
    
    if format_sheets:
        # Read the first matching sheet
        df = pd.read_excel(xls, sheet_name=format_sheets[0])
    else:
        # Read the first sheet if no "format" sheet exists
        df = pd.read_excel(xls, sheet_name=0)
except Exception as e:
    print(f"Error: {e}")
    
df.columns=df.columns.str.lower()
obs    = df['obs'][0]
target = df['target'][0]
target = target.replace("/", "")
expname= df['exp'][0]

head   = expname+","+obs+","+target+" target"
if 'sig' in obs:
    obs = 's'
elif obs=='f2' or obs=="F2":
    obs = ''

f2  = np.array(df["value"])
xbj = np.array(df["x"])
q   = np.array(df["q2"])


#init arrays 
dummy=np.zeros(len(q))
eb  = 0*dummy
stat= 0*dummy
eru = 0*dummy #uncorrelated
erc = 0*dummy #correlated
sys = 0*dummy

norm = 0 #fractional

# CJ header format:
# exp name, target
# comments
# *
# norm in fraction, number of cor errors
# x, Q2, f2, i, stat_u, syst_tot, syst_u, cor1, cor2, ...

# syst_tot will be all non-stat_u errors sumed. When flag =2 (using correlated error), cj fitpack will ignore this syst_tot
# one more coloumn for all uncorrelated syst errors summed
# one column for each correlated error (in %)

nc = 0
cor = []

for col in df.columns:
    st = col
    if 'elab' in col:
        eb = np.array(df[col])

    if 'norm_c' in col:
        temp = np.array(df[col])
        if '%' in col:
            norm=temp[0]/100.
        else:
            norm=temp[0]/f2[0]
        break

    elif 'stat_u' in col or "dFST_u" in col:
        stat=np.array(df[col])
        if '%' in col:
            stat=stat/100.*f2
        
    elif '_u' in col:
        temp = np.array(df[col])
        if '%' in col:
            temp = temp/100.*f2
        eru = eru**2 + temp**2
        sys += temp**2

    elif '_c' in col:
        temp=np.array(df[col])
        if not('%' in col):
            temp=temp/f2*100.
        sys+=temp**2

        st = st[:-2] ## remove _c in cor name
        w = 0
        if "%" in st:
            w +=1
        if "*" in st:
            w +=1
        st = st[w:]
        cor.append((st, temp))
        nc +=1


eru=np.sqrt(eru) # all uncorrelated error except stat
sys=np.sqrt(sys) # all errors except stat

if nc <1 :
    out = [('x',xbj),('Q2',q),('F2',f2),('Ebeam',eb),('stat',stat),('sys_tot',sys),('dummy',dummy),('dummy',dummy)]

else:
    out = [('x',xbj),('Q2',q),('F2',f2),('Ebeam',eb),('stat',stat),('sys_tot',sys),('sys_u',eru)]
    out=out+cor

df2 = pd.DataFrame(dict(out))

# follow CJ15 convention, drop the last 8 points which has large chi2
if expname=='hermes':
	df2 = df2[:-8] 

#	print out
out_dir = "to_cj_output/"
os.makedirs(out_dir,exist_ok=True)

output = out_dir+expname+'_'+obs+target
with open(output, 'w') as outfile:
    outfile.write('%s\n%s\n*\n %5.4f  %d\n' % (head,f'converted from {exp_id}',norm,nc))
    df2.to_string(outfile,index=False)

print(f"Done! Please check {output}")
