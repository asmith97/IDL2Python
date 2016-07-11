import numpy as np






def ligand_length_distribution(data, chain_length, nligands):
	startpos = (chain_length - 1) * nligands
	ligands = np.add(range(nligands),startpos)
	l_low = min(ligands)
	l_high = max(ligands)






ligand_length_distribution(0,12,471)