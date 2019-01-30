#########
# about #
#########

__version__ = "0.1.1"
__author__ = ["Nikos Karaiskos", "Mor Nitzan"]
__status__ = "beta"
__licence__ = "GPL"
__email__ = ["nikolaos.karaiskos@mdc-berlin.de", "mornitz@gmail.com"]

###########
# imports #
###########

from novosparc import *

if __name__ == '__main__':

    ###################################
    # 1. Import and subset the data ###
    ###################################
    start_time = time.time()
    print ('Loading data ... ', end='', flush=True)

    # Read the BDTNP database
    gene_names = np.genfromtxt('datasets/bdtnp/dge.txt', usecols=range(6, 82),
                          dtype='str', max_rows=1)
    dge = np.loadtxt('datasets/bdtnp/dge.txt', usecols=range(84), skiprows=1)

    # Optional : downsample number of cells
    num_cells = int(np.random.randint(504, 800, 1)) 
    cells_selected = np.random.choice(dge.shape[0], num_cells, replace=False)
    dge = dge[cells_selected, :]
    
    # Choose a number of markers to use for reconstruction
    num_markers = int(np.random.randint(1, 5, 1))
    markers_to_use = np.random.choice(dge.shape[1], num_markers, replace=False)

    print ('done (', round(time.time()-start_time, 2), 'seconds )')
    
    ################################
    # 2. Set the target space grid #
    ################################

    print ('Reading the target space ... ', end='', flush=True)    
    # Read and use the bdtnp geometry
    locations = np.loadtxt('datasets/bdtnp/geometry.txt', usecols=range(3), skiprows=1)
    locations = locations[:, [0, 2]]
    locations = locations[cells_selected, :] # downsample to the cells selected above
    print ('done')

    ######################################
    # 3. Setup for the OT reconstruction #
    ######################################
    
    cost_expression, cost_locations = setup_for_OT_reconstruction(dge[:, np.setdiff1d(np.arange(dge.shape[1]), markers_to_use)],
                                                                  locations, 5)
    cost_marker_genes = cdist(dge[:, markers_to_use]/np.amax(dge[:, markers_to_use]),
                              dge[:, markers_to_use]/np.amax(dge[:, markers_to_use]))

    #############################
    # 4. Spatial reconstruction #
    #############################

    start_time = time.time()
    print ('Reconstructing spatial information with', num_markers,
           'markers:', num_cells, 'cells and',
           locations.shape[0], 'locations ... ')
    
    # Distributions at target and source spaces
    p_locations = ot.unif(len(locations))
    p_expression = ot.unif(num_cells)

    alpha_linear = 0.5
    gw = gwa.gromov_wasserstein_adjusted_norm(cost_marker_genes, cost_expression, cost_locations,
                                              alpha_linear, p_expression, p_locations,
                                              'square_loss', epsilon=5e-4, verbose=True)
    sdge = np.dot(dge.T, gw)
    
    print (' ... done (', round(time.time()-start_time, 2), 'seconds )')

    #########################################
    # 5. Write data to disk for further use #
    #########################################

    start_time = time.time()
    print ('Writing data to disk ...', end='', flush=True)

    np.savetxt('output_bdtnp/sdge_' + str(num_cells) + '_cells_'
               + str(locations.shape[0]) + '_locations.txt', sdge, fmt='%.4e')

    print ('done (', round(time.time()-start_time, 2), 'seconds )')

    ###########################
    # 6. Plot gene expression #
    ###########################

    gene_list_to_plot = ['ftz', 'Kr', 'sna', 'zen2']
    plot_gene_patterns(locations, sdge, gene_list_to_plot,
                       folder='output_bdtnp/',
                       gene_names=gene_names, num_cells=num_cells)

    ###################################
    # 7. Correlate results with BDTNP #
    ###################################
    
    corel = sum([pearsonr(sdge[x, :], dge[:, x])[0] for x in range(76)])/76

    with open('output_bdtnp/results.txt', 'a') as f:
        f.write('number_cells,,number_markers,pearson_correlation' + '\n')
        if sum(sum(sdge)) > 1:
            f.write(str(num_cells) + ',' + str(num_markers) + ','
                    + str(round(corel, 2)) + '\n')













    


