import pandas as pd
import pandas.io.sql as psql
import random
from decimal import *
from scipy import stats
import urllib2
from StringIO import StringIO
from zipfile import ZipFile

# Download Annual Extract of Tax-Exempt Organization Financial Data for 2013 from the IRS.
# http://www.irs.gov/uac/SOI-Tax-Stats-Annual-Extract-of-Tax-Exempt-Organization-Financial-Data
request = urllib2.Request('http://www.irs.gov/file_source/pub/irs-soi/13eofinextract990.zip')
request.add_header('Accept-encoding', 'zip')
response = urllib2.urlopen(request)

# Unzip file
z = ZipFile(StringIO(response.read()))
f = z.open('py13_990.dat')

# Read file into Pandas dataframe
df = pd.read_table(f, index_col='EIN', delimiter=' ', usecols=['EIN', 'politicalactvtscd', 'noemplyeesw3cnt', 'totrevenue'])

# Filter organizations reporting no employees.
df = df[(df.noemplyeesw3cnt != 0)]

# Calculate revenue per employee.
df['revpercap'] = df['totrevenue'] / df['noemplyeesw3cnt'] 

# Get the mean of revenue per employee for organizations
# reporting political activity and the mean for organizations 
# not reporting political activity.
political = df.revpercap[(df.politicalactvtscd == 'Y')]
nonpolitical = df.revpercap[(df.politicalactvtscd == 'N')]
politicalMean = political.mean()
nonpoliticalMean = nonpolitical.mean()

# Difference in means and the size of the samples.
delta = abs(politicalMean - nonpoliticalMean)
pcount = political.count()
ncount = nonpolitical.count()

# Sanity check 
print 'Sanity check:\n\nnonpoliticalMean: %s \npoliticalMean: %s \ndelta: %s \npcount: %s \nncount: %s\n\n\n' % (nonpoliticalMean, politicalMean, delta, pcount, ncount)

sampleDeltas = []

for x in range(1000):
    
    pSizedSample = random.sample(df.index, pcount)
    nSizedSample = random.sample(df.index, ncount)
    pSampleMean = df.ix[pSizedSample].revpercap.mean()
    nSampleMean = df.ix[nSizedSample].revpercap.mean()
    sampleDelta = abs(pSampleMean - nSampleMean)
    sampleDeltas.append(sampleDelta)

samplesOutsideDelta = [s for s in sampleDeltas if s > delta]
p = Decimal(len(samplesOutsideDelta))/ Decimal(len(sampleDeltas))

print 'p-value: %s\n\n' % p.quantize(Decimal(10) ** -4)
