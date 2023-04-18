model Tuto3D

global {
	int nb_cells <- 4;
	int environment_size <- 5;
	geometry shape <- cube(environment_size);

	init {
		create cell number: nb_cells {
			location <- {rnd(environment_size), rnd(environment_size), rnd(environment_size)};
		}
	}

	action step {
	    write "step";
	}
}

species cell skills: [moving3D] {
    map action_space;
    init {
        action_space <- [];
    }

	action do_move (float velocity, int heading) {
        do move speed: velocity heading: heading;
    }

    reflex random_move {
        do do_move velocity: 0.01 heading: rnd(360);
    }

	aspect default {
		draw sphere(environment_size * 0.01) color: #blue;
	}


}

experiment particles_experiment type: gui {
	parameter "Initial number of cells: " var: nb_cells min: 1 max: 1000 category: "Cells";
	output {
		display View1 type: 3d {
			graphics "env" {
				draw cube(environment_size) color: #black wireframe: true;
			}
			species cell;
		}
	}
}