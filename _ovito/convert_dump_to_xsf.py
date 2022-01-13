# convert last timestep structure to xsf file
from ovito.io import import_file, export_file

def get_last_frame_xsf_file(_dir):
    pipeline = import_file(f'{_dir}/traj.dump')
    frame = pipeline.source.num_frames
    # export_file(pipeline, f"{_dir}/output.dump", "lammps/dump", frame=frame)
    export_file(pipeline, f"{_dir}/output.xyz", "xyz", columns =
      ["Particle Type", "Position.X", "Position.Y", "Position.Z"],
                frame=frame
    )
    def get_lattice_arr(lattice_line):
        lattice = lattice_line.split(' Origin')[0].split('"')[1].split(' ')
        lattice_arr = []
        arr = []
        for i, elm in enumerate(lattice):
            arr.append(elm)
            if (i+1) % 3 == 0:
                lattice_arr.append(arr)
                arr = []
        return lattice_arr

    with open(f'{_dir}/output.xyz', 'r') as f:
        l_strip = [s.strip() for s in f.readlines()]
        natom = l_strip[0]
        lattice = get_lattice_arr(l_strip[1])
        coord = l_strip[2:]
        with open(f'{_dir}/last_structure.xsf', 'w') as lf:
            lf.write('CRYSTAL\n')
            lf.write('PRIMVEC\n')
            for l in lattice:
              lf.write(f'{" ".join(l)}\n')
            lf.write('PRIMCOORD\n')
            lf.write(f' {natom} 1\n')
            for l in coord:
                lf.write(f'{l}\n')