/**
* Name: Salzburghotelsmuseums
* Based on the internal skeleton template.
* Author: anivjicma
* Tags:
*/

model Salzburghotelsmuseums

global {
	/** Insert the global definitions, variables and actions here */
	int port;
	float step <- 5 #mn;
	geojson_file bounds_3857_geojson_file <- geojson_file("/TouristFlow/includes/Data/2022-07-04_bounds_3857.geojson");
	geometry shape <- envelope(bounds_3857_geojson_file);

	graph the_graph;
	int nb_people_alive -> {length(people)};

	string start_datestring <- "2018-01-01";
	date starting_date <- date(start_datestring);
	string end_datestring <- "2019-01-02";
	date end_date <- date(end_datestring);

//	variables required for the movement of people
	float min_visiting_start <- 8.0;
	float max_visiting_start <- 12.0;
	float min_visiting_end <- 16.0;
	float max_visiting_end <- 20.0;
	float min_speed <- 1.0 #km / #h;
	float max_speed <- 5.0 #km / #h;


	file basemap <- image_file("/TouristFlow/includes/Data/basemap.jpg");

	reflex halt when: not until(end_date) {
		do die;
	}

	init{
		create accommodation from: geojson_file("/TouristFlow/includes/Data/accommodation_3857_clipped.geojson") with: [capacity::int(read("capacity")) ] {
			capacity <- capacity;
		}

		create attraction from: geojson_file("/TouristFlow/includes/Data/2022-07-06_salzburg-card-pois_3857.geojson")
			with: [
				name::read ("AKZName"),
				display_name::read ("Name")
			] {
			name <- name;
			opening_time <- 8.0;
			closing_time <- 20.0;
			capacity <- 100;
		}

		create road from: geojson_file("/TouristFlow/includes/Data/highways_clean_network.geojson");
		the_graph <- as_edge_graph(road);

		string csvfilename <- "/TouristFlow/includes/Data/agents_for_GAMA_2018/agents_for_GAMA_" + start_datestring + ".csv";

		create people from: csv_file(csvfilename, ';', '"', true) with: [
			knr::read("knr"),
			ktyp::read("ktyp"),
			ausname::read("ausname"),
			visited_places_names::eval_gaml(read("visited_places_names"))
		]{
			knr <- knr;
			ktyp <- ktyp;
			ausname <- ausname;
			visited_places_names <- visited_places_names;
			agent_date <- current_date;
			needs_prediction <- false;
			needs_to_ask <- false;
		}

		inspect people(2);
	}


	reflex load_agents_for_new_day when: current_date.day != starting_date.day {
			string save_data <- 'poi_name, knr, datetime \n';
			ask attraction {
				loop a over: self.checkins {
					string csvrow <- self.name + ',' + a[0] + ',' + a[1] + '\n';
					save_data <- save_data + csvrow;
				}
				self.checkins <- nil;
//				write 'POI '+ self.name + ' resetting!';
			}
			save save_data to: 'pois_' + string(starting_date,'yyyy-MM-dd') + '.csv' format: csv rewrite: true;

			starting_date <- current_date;
			string datestring <- string(starting_date,'yyyy-MM-dd');
			string csvfilename <- "/TouristFlow/includes/Data/agents_for_GAMA_2018/agents_for_GAMA_" + datestring + ".csv";

			create people from: csv_file(csvfilename, ';', '"', true) with: [
				knr::read("knr"),
				ktyp::read("ktyp"),
				ausname::read("ausname"),
				visited_places_names::eval_gaml(read("visited_places_names"))
			]{
				knr <- knr;
				ktyp <- ktyp;
				ausname <- ausname;
				visited_places_names <- visited_places_names;
				agent_date <- current_date;
				needs_prediction <- false;
				needs_to_ask <- false;
			}
	}

	map<string, int> get_observation {
		map<string,int> obs <- [];
		loop visitor over: people {
			write self.name;
			string vis_name <- self.name;
			add vis_name::1 to: obs;
    	}
    	return obs;
	}
}

species buildings{
	rgb color;
	int capacity;
	string name;
	aspect base {
		draw shape color:color;
	}
}


species accommodation parent: buildings{
	rgb color <- #blue;
}


species attraction parent: buildings{
	geometry shape <- circle(20);
	rgb color <- #red;
	float opening_time;
	float closing_time;
	int capacity <- 100;
	string display_name;
	list<list<string>> checkins;
//	list<date> checkin_times;


//	reflex check_in{
//		list<string> knrs <- people accumulate (each.knr) where (intersects(geometry(each), self));
//		add knrs to: checkin_knrs;
//		add current_date to: checkin_times;
//	}

}


species road parent: buildings skills: [skill_road]{
	rgb color <- #black;
}


species people skills: [moving] {
	geometry shape <- circle(4);
	rgb color <- #yellow;
	rgb color_border <- #black;
	accommodation sleeping_place;
	attraction visiting_place;
	buildings the_target <- nil ;
	list<string> visited_places_names;
//	list<string> simulated_check_ins;
	list<string> received_predictions;
	float start_visiting;
	float end_visiting ;
	float visit_duration;
	float check_out_time;
	string knr;
	string ktyp;
	string ausname;
	string prediction;
	date agent_date;
	bool objective_visiting <- false;
	bool needs_prediction <- false;
	bool needs_to_ask <- false;
	bool checked_in <- false;

	init {
		speed <- 5 #km/#h;
		start_visiting <- rnd(min_visiting_start, max_visiting_start);
		end_visiting <- rnd(min_visiting_end, max_visiting_end);
		sleeping_place <- one_of(accommodation);
		location <- any_location_in(sleeping_place);
	}

	aspect base{
		draw shape color: color border: color_border;
	}

	reflex move when: the_target != nil {
		do goto target: the_target on: the_graph recompute_path: false;
		if intersects(the_target,location){
			the_target <- nil;
		}
	}

	reflex time_to_start_visiting when:  objective_visiting = false and (current_date.hour + current_date.minute/60) >= start_visiting and (current_date.hour + current_date.minute/60) < end_visiting {
		objective_visiting <- true;
		needs_prediction <- true;
		needs_to_ask <- true;
	}

	reflex time_to_go_home when: objective_visiting = true and (current_date.hour + current_date.minute/60) >= end_visiting {
//		to speed up simulations - I can just kill people instead of sending them back to the hotel
		do die;
//		the_target <- sleeping_place;
//		objective_visiting <- false;
//		checked_in <-false;
//		check_out_time <- nil;
//		needs_prediction <- false;
//		visiting_place <- nil;
//		prediction <- nil;
	}

	reflex visit_predicted_poi when: prediction != nil {
		if prediction = 'Final' {
			do die;
		}
		else{
			visiting_place <- attraction first_with (each.name = prediction);
			the_target <- visiting_place;
	//		keep track of visited places
//	Here I will need to implement the average time spent at a POI that I got from Marvin.. Somehow the stay of the agent at a POI needs to be randomized from these values
			add prediction to: received_predictions;
			prediction <- nil;
			needs_prediction <- false;
		}
	}

	reflex check_in when: checked_in = false and self intersects self.visiting_place {
		list<string> checkin_data <- list(self.knr, string(current_date));
		add checkin_data to: self.visiting_place.checkins;
		add visiting_place.name to: visited_places_names;
//		add visiting_place.name to: simulated_check_ins;
		visit_duration <- rnd(1.0, 4.0);
		check_out_time <- current_date.hour + current_date.minute/60 + visit_duration;
		checked_in <- true;
	}

	reflex check_out when: checked_in = true and (current_date.hour + current_date.minute/60) >= check_out_time {
		self.visiting_place <- nil;
		checked_in <- false;
		needs_prediction <- true;
		needs_to_ask <- true;
		check_out_time <- nil;
	}

	reflex visit_random when: prediction = nil and visiting_place = nil and needs_prediction = true {
		trace {
			int num_attractions <- length(attraction);
			write "Num Attraction: " + num_attractions;
			if num_attractions > 0 {
				int attraction_idx <- rnd(length(attraction)-1);
				write "Selected attraction no. " + attraction_idx;
				attraction selected_attraction <- species(attraction).population[attraction_idx];
				write selected_attraction;
				write "Attraction has name " + selected_attraction.name;
				prediction <- selected_attraction.name;
			}
		}
	}

//	reflex die_when_day_ends when: current_date.day != agent_date.day{
//		// write "Agent " + self + "dieing due to end of day " + agent_date;
////		do die;
//		objective_visiting <- false;
//		visiting_place <- nil;
//		the_target <- sleeping_place;
//	}
}


species tcp_prediction_getter skills: [network] {
	list<people> agents_needing_prediction -> people where(each.needs_prediction = true);
	list<people> agents_need_to_ask -> people where(each.needs_to_ask = true);

	int my_port;
	list<string> knrs_needing_prediction;



    action send_observation {

    	// ---------------------- EDIT OBSERVATION HERE ----------------------------------------------------------------------------------
    	people asking <- first(agents_need_to_ask);
    	string msg <- "{'id':'" +asking.name
    		+"', 'date': '"+ current_date
    		//+', "preferences":'+asking.
    		//+', "ticket_length":"'+asking.
    		+"', 'ticket_type':'"+asking.ktyp
    		+"','visited':"+asking.visited_places_names+"}";

		write "Sent to network: " + msg;
		do send to:"localhost:"+port contents: msg + "\n";
		asking.needs_to_ask <- false;
		return asking;
    }

   	 message wait_next_message {
		write "waiting for python to send data";
		loop while: !has_more_message()  {
			do fetch_message_from_network;
		}

		message msg <- fetch_message();
		write "GAMA received: " + msg;
		return msg;
	}

	reflex print_agents_needing_prediction when: length(agents_needing_prediction) > 0 {
	    people asked <- send_observation();
		let msg <- wait_next_message();
		string current_prediction  <- nil;
		if msg != nil {
				current_prediction <- eval_gaml(msg.contents);
		}

		ask asked {
			self.prediction <- current_prediction;
		}
	}
}

experiment Salzburghotelsmuseums type: gui {
	/** Insert here the definition of the input and output of the model */
	parameter "port" var:port init:0;
	parameter "Step:" var: step category: simulation;
	parameter "Start date:" var: start_datestring category: simulation;
	parameter "End date:" var: end_datestring category: simulation;
 	output {
 		monitor "date" value: string(current_date.date, 'yyyy-MM-dd') refresh: every(1#day);
 		monitor "time" value: string(current_date, 'HH:mm') refresh: every(1#cycle);
		monitor "datetime" value: current_date;
		monitor "knrs" value: tcp_prediction_getter accumulate (each.knrs_needing_prediction);
	//	monitor "predictions" value: tcp_prediction_getter accumulate (each.response_map);
		monitor "number of people alive" value: nb_people_alive;
 		display city_display type: opengl{
 			image 'basemap' file: basemap.path;
 			species accommodation aspect: base;
 			species attraction aspect: base;
 			species road aspect: base;
 			species people aspect: base;
 		}
 	}
}