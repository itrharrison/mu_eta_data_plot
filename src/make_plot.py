import numpy as np
import pdb
import os
import itertools

from astropy.table import Table

from matplotlib import pyplot as plt
from matplotlib import rc
import matplotlib as mpl

from palettable.wesanderson import Zissou_5
clist = Zissou_5.mpl_colors

rc('text', usetex=True)
rc('font', family='serif')
rc('font', size=11)
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=clist[::-1]) 

plt.close('all') # tidy up any unshown plots
plt.figure(1, figsize=(2*4.5, 3.75))

make_runs = True
mgcamb_dir = '/Users/ianharrison/Dropbox/code_cdf/MGCAMB/src/'
A_lens = 1.15

# some possibly interesting model values from Fig. 31 of arXiv:1807.06209
# etas: 1, 0., 2. 1.6, 0.1
# mus: 1., 2., -1.5, 1.19, 0.68

# eta - 1, mu - 1: (-0.1, 0.4), (1.0, 0.0), (1.1, -0.3), (2., -0.4)
# eta, mu: (0.9, 1.4), (2.0, 1.0), (2.1, 0.7), (3., 0.6)

models = [
          {'mu0' : 1.0, 'eta0' : 1.0}, # GR
          {'mu0' : 1.4, 'eta0' : 0.9},
          {'mu0' : 1.0, 'eta0' : 2.0},
          {'mu0' : 0.7, 'eta0' : 2.1},
          {'mu0' : 0.6, 'eta0' : 3.0},
          ]

params_template_fname = 'inis/params.template'

for model in models:

    if not os.path.exists('./HighLExtrapTemplate_lenspotentialCls.dat'):

        os.system('ln -s {}HighLExtrapTemplate_lenspotentialCls.dat .'.format(mgcamb_dir))

    
    run_name = 'mu{0:.2f}_eta{1:.2f}'.format(model['mu0'], model['eta0'])

    params_filename = 'inis/params_tests_{0}.ini'.format(run_name)

    params_template = open(params_template_fname).read()

    params_file = params_template.format(run_name='./output/' + run_name,
                                         mu0=model['mu0'] - 1,
                                         eta0=model['eta0'] - 1)

    open(params_filename, 'w').write(params_file)

    cmd = '{0}camb {1}'.format(mgcamb_dir, params_filename)
    if make_runs:
        os.system(cmd)

    plt.subplot(121)

    cmb_data = Table.read('output/{0}_lensedCls.dat'.format(run_name), format='ascii')
    plt.plot(cmb_data['L'], cmb_data['TT'], '-', )

    plt.subplot(122)

    # lensing_data = Table.read('output/{0}_scalCls.dat'.format(run_name), format='ascii')
    lensing_data = Table.read('output/{0}_lenspotentialCls.dat'.format(run_name), format='ascii')
    # plt.plot(lensing_data['L'], lensing_data['PP'], '-', )

    if model['mu0']==1.0 and model['eta0']==1.0:
        # name_str = run_name.split('_')[0].replace('mu','$\\mu_{0}$ = ') + ' ' + run_name.split('_')[1].replace('eta','$\\eta_{0}$ = ') + ' ' + '(GR + $A_{\\rm lens} = 1.15$)'
        name_str = '(GR + $A_{\\rm lens} = 1.15$)'
        plt.plot(lensing_data['L'], lensing_data['PP'] * A_lens, '-', label=name_str, zorder=-10)
    else:
        name_str = run_name.split('_')[0].replace('mu','$\\mu_{0}$ = ') + ' ' + run_name.split('_')[1].replace('eta','$\\eta_{0}$ = ')
        plt.plot(lensing_data['L'], lensing_data['PP'], '-', label=name_str)

plt.subplot(121)

cmb_data = Table.read('data/COM_PowerSpect_CMB_R2.02.fits', hdu=7)
cmb_data_lowell = Table.read('data/COM_PowerSpect_CMB_R2.02.fits', hdu=1)
plt.errorbar(cmb_data['ELL'], cmb_data['D_ELL'], yerr=cmb_data['ERR'], fmt='o', markersize=3, label=None, color='k')
plt.errorbar(cmb_data_lowell['ELL'], cmb_data_lowell['D_ELL'], yerr=[cmb_data_lowell['ERRDOWN'], cmb_data_lowell['ERRUP']], fmt='o', markersize=3, label=None, color='k')

# cmb_data = Table.read('data/COM_PowerSpect_CMB-TT-binned_R3.01.txt', format='ascii')
# plt.errorbar(cmb_data['l'], cmb_data['Dl'], yerr=(cmb_data['-dDl'], cmb_data['+dDl']), fmt='o', markersize=3, label=None, color='k')

plt.xscale('log')
plt.xlabel('$l$')
plt.ylabel('$\mathcal{D}^{TT}_l$')
plt.xlim([2,2000])

plt.subplot(122)

lensing_data = Table.read('data/smicadx12_Dec5_ftl_mv2_ndclpttptt_p_teb_agr2_bandpowers.dat', format='ascii')

lensing_xm = lensing_data['L_av'] - lensing_data['L_min']
lensing_xp = lensing_data['L_max'] - lensing_data['L_av']

plt.errorbar(lensing_data['L_av'], lensing_data['PP'], yerr=lensing_data['Error'], xerr=(lensing_xm, lensing_xp), fmt='o', markersize=3, label=None, color='k')

plt.ylabel('$\mathcal{D}^{\phi \phi}_L$')
plt.xscale('log')
plt.xlim([8,2048])
plt.ylim([-0.5e-7, 2.e-7])
plt.xlabel('$L$')
plt.axhline(0., linestyle='dashed', color='k', alpha=0.4)

plt.legend(numpoints=1, fontsize='small', loc='lower left')

plt.subplots_adjust(wspace=0.25)

plt.savefig('plots/test_models.png', dpi=300, bbox_inches='tight')
