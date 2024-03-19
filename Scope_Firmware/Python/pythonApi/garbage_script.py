from electrode_names import ElectrodeNames

electrode_ids = ElectrodeNames.parse_electrode_input("A1-B12,D9-D12,H4-H5,H6,H8,H9")
ElectrodeNames.ascii_art_selected(electrode_ids)
