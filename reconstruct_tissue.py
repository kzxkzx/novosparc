###########
# imports #
###########

import novosparc
import time
import numpy as np
from scipy.spatial.distance import cdist
from scipy.stats import pearsonr

if __name__ == '__main__':

    ###################################
    # 1. Import and subset the data ###
    ###################################
    start_time = time.time()
    print ('Loading data ... ', end='', flush=True)

    # Read the gene names from the DGE. Assumes that the DGE is formatted
    # with genes are rows and cells as columns.
    gene_names = np.genfromtxt('/pathto/dge.txt',
                               usecols=range(1), dtype='str', skip_header=True)
    # Read the DGE itself. Read only a maximum number of cells.
    max_cell_number = 1000
    dge = np.loadtxt('/pathto/dge.txt',
                     usecols=range(1, max_cell_number), skiprows=1)
    
    # Optional: downsample number of cells.
    cells_selected, dge = novosparc.pp.subsample_dge(dge, 500, 800)
    num_cells = dge.shape[0]

    # Optional: Subset to the highly variable genes or other set of genes
    high_var_genes = np.genfromtxt('/pathto/hvg.txt', dtype='str')
    dge = dge[np.nonzero(np.in1d(gene_names, high_var_genes))[0], :]
    dge = dge.T
    print ('done (', round(time.time()-start_time, 2), 'seconds )')


    ################################
    # 2. Set the target space grid #
    ################################

    print ('Constructing the target grid ... ', end='', flush=True)

    # Construct a square target grid or read it if available
    locations = novosparc.rc.construct_target_grid(num_cells)
    
    print ('done')


    ######################################
    # 3. Setup for the OT reconstruction #
    ######################################

    cost_expression, cost_locations = novosparc.rc.setup_for_OT_reconstruction(dge, locations, 5)


    #############################
    # 4. Spatial reconstruction #
    #############################

    start_time = time.time()
    print ('Reconstructing spatial information for',
           num_cells, 'cells and', locations.shape[0], 'locations ... ')

    # Distributions at target and source spaces. If unkown uniform distributions
    # should be used.
    p_locations, p_expression = novosparc.rc.create_space_distributions(len(locations), num_cells)

    # alpha parameter controls the reconstruction. Set 0 for de novo, between
    # 0 and 1 in case markers are available.
    alpha_linear = 0

    # Compute the mapping probabilities for each cell.
    gw = gwa.gromov_wasserstein_adjusted_norm(1, cost_expression, cost_locations,
                                              alpha_linear, p_expression, p_locations,
                                              'square_loss', epsilon=5e-4, verbose=True)
    # Compute the sDGE.
    sdge = np.dot(dge_full.T, gw)

    print (' ... done (', round(time.time()-start_time, 2), 'seconds )')

    
    #########################################
    # 5. Write data to disk for further use #
    #########################################

    start_time = time.time()
    print ('Writing data to disk ...', end='', flush=True)

    np.savetxt('output/genes.txt', gene_names, fmt='%s')
    np.savetxt('output/high_var_genes.txt', high_var_genes, fmt='%s')
    np.savetxt('output/grid_' + shape + '_' + str(num_cells) + '_cells_'
                   + str(locations.shape[0]) + '_locations.txt', locations, fmt='%.4e')
    np.savetxt('output/sdge_' + str(num_cells) + '_cells_'
                   + str(locations.shape[0]) + '_locations.txt', sdge, fmt='%.4e')

    print ('done (', round(time.time()-start_time, 2), 'seconds )')


    ###########################
    # 6. Plot gene expression #
    ###########################

    gene_list_to_plot = ['gene1', 'gene2']
    novosparc.pl.plot_gene_patterns(locations, sdge, gene_list_to_plot,
                                    folder='output/', gene_names=gene_names)
    
