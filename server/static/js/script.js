
// *********************************************
//
// GLOBAL VARIABLES
// ----------------
// These variables are setting the defaults for
// the user defined variables.
//
// *********************************************
/** @global */
var MIN_TEMP = 0; // Minimum temperature allowed
var MAX_TEMP = 200;  // Maximum temperature allowed
var MIN_AMP = 100; // Minimum amplification size allowed
var MAX_AMP = 1000; // Maximum amplification size allowed
var MIN_PERCENT = 0; // Minimum percentage recoded allowed
var MAX_PERCENT = 100; // Maximum percentage recoded allowed
var NUCLEOTIDES = ['a','c','g','t']; // Nucleotides supported
var GENE_BEGINING = 1;
var GENE_END = 100;
var KMER_SIZE = 24;
var NA_CONCENTRATION = 1; // Can become an advanced parameter
var FIRST_NUC_SUB_SCORE = 1; // Score value if there is a substitution possible on the first nucleotide of the codon
var SECOND_NUC_SUB_SCORE = 1; // Score value if there is a substitution possible on the second nucleotide of the codon
var THIRD_NUC_SUB_SCORE = 1; // Score value if there is a substitution possible on the third nucleotide of the codon

// *********************************************
//
// This is the default standard amino acid table
// set as a global variable
//
// *********************************************
/** @global */
var AA_TABLE = {
	A:["GCT","GCC","GCA","GCG"],
	R:["AGA","AGG","CGT","CGC","CGA","CGG"],
	N:["AAT","AAC"],
	D:["GAT","GAC"],
	C:["TGT","TGC"],
	Q:["CAA","CAG"],
	E:["GAA","GAG"],
	G:["GGT","GGA","GGC","GGG"],
	H:["CAT","CAC"],
	I:["ATT","ATC","ATA"],
	L:["TTA","TTG","CTT","CTC","CTA","CTG"],
	K:["AAA","AAG"],
	M:["ATG"],
	F:["TTT","TTC"],
	P:["CCT","CCC","CCA","CCG"],
	S:["AGT","AGC"],
	T:["ACT","ACC","ACA","ACG"],
	W:["TGG"],
	Y:["TAT","TAC"],
	V:["GTT","GTC","GTA","GTG"],
	STOP:["TAA","TAG","TGA"]
};

// *********************************************
//
// Default codon table (human)
//
// *********************************************
/** @global */
var CODON_TABLE = {
	AAA:"K",AAC:"N",AAG:"K",AAT:"N",TTT:"F",TTC:"F",TTA:"L",TTG:"L",CTT:"L",CTC:"L",CTA:"L",CTG:"L",
	ATT:"I",ATC:"I",ATA:"I",ATG:"M",GTT:"V",GTC:"V",GTA:"V",GTG:"V",TCT:"S",TCC:"S",TCA:"S",TCG:"S",
	CCT:"P",CCC:"P",CCA:"P",CCG:"P",ACT:"T",ACC:"T",ACA:"T",ACG:"T",GCT:"A",GCC:"A",GCA:"A",GCG:"A",
	TAT:"Y",TAC:"Y",TAA:"STOP",TAG:"STOP",CAT:"H",CAC:"H",CAA:"Q",CAG:"Q",GAT:"D",GAC:"D",GAA:"E",GAG:"E",
	TGT:"C",TGC:"C",TGA:"STOP",TGG:"W",CGT:"R",CGC:"R",CGA:"R",CGG:"R",AGT:"S",AGC:"S",AGA:"R",AGG:"R",
	GGT:"G",GGC:"G",GGA:"G",GGG:"G"
};

// *********************************************
//
// GLOBAL FUNCTIONS
// ----------------
// These are documented via jsdoc
//
// *********************************************


/**
 * Core functionality for generating watermarks
 * 
 */
	function calculateWatermarks () {
	
		  //
		  // Call for the set of validation functions to make sure
		  // all parameters are acceptable.
		  //
		var failed = validateAll ();
		if (failed) {
			console.log("DEVELOPER: Failed form validation.");
			return;
		} else {
			console.log("DEVELOPER: Passed form validation.");
		}
	
		  // **************************************************************** 
		  // Grab the different form entries now that everything is validated
		  // ****************************************************************
		
		  //
		  // Grab the genomic sequence from the form
		  //
		var genomic_sequence = document.getElementById("genomic_sequence").value;
		genomic_sequence = genomic_sequence.replace(/(" "|\r\n|\n|\r)/gm,"");
		  // Create the parts of the genome that are going to be tested
		  // This will change the nucleotide sequence to toUpperCase
		  // and remove spaces
		  // #WARNING - should add replacement of U to T here?
		var truncated_genomic_sequence = genomic_sequence.toUpperCase();
		truncated_genomic_sequence = truncated_genomic_sequence.replace(/\s+/g, '');
		
		  //
		  // Grab the additional variables from the HTML form.
		  //
		var minimum_melting_temp = parseInt(document.getElementById("minimum_melting_temp").value);
		var maximum_melting_temp = parseInt(document.getElementById("maximum_melting_temp").value);
		var minimum_amplification = parseInt(document.getElementById("minimum_amplification").value);
		var maximum_amplification = parseInt(document.getElementById("maximum_amplification").value);
		var minimum_recoded = parseInt(document.getElementById("minimum_recoded").value);

		  //
		  // Get organism type
		  //
		var organism = document.getElementById("organism").value;
		  // Set the organism codon table
		setCodonTable(organism);
		
		
		  // Convert triplets to amino acids
		  // Need codon table
		  // Start grabbing triplets and deciding the level of change allowed.
		var full_map = new Array();
		
		  // Loop through the sequences and create the codon table _map
		  // Can call amino acid via codon or call codons via amino acid
		for (var i = 0; i < (truncated_genomic_sequence.length / 3); i++) {
			var _codon = truncated_genomic_sequence.substring((i * 3), ((i + 1) * 3));
			if (_codon.length < 3) continue;
			
			var _aa = CODON_TABLE[_codon];
			var _map = {
					    codon:_codon,
					    aa:_aa
					    };
			full_map.push(_map);
		}
		
		  // Generate kmers
		  // Each kmer should get a score
		
		var kmer_scores = new Array();
		var kmer_map = new Array();
		var kmer_counter = 0;
		var meltingTempCount = 0;
		var percentChangedCount = 0;
		
		for (var i = 0; i < full_map.length; i++) {
			kmer_map.push(full_map[i]);
			if (kmer_map.length > (KMER_SIZE / 3)) {
				kmer_map.shift();
			}
			if (kmer_map.length == (KMER_SIZE / 3)) {
				// Have a kmer of length KMER_SIZE
				// Need to determine a score
				// Also need new nucleotides that match the score
				var new_kmer = new Array();
				var counter = 0;

				for (var j = 0; j < kmer_map.length; j++) {
					var _all_codons = AA_TABLE[kmer_map[j].aa];
					var score = new Array();
					var top_score = {score:0,position:0,codon:kmer_map[j].codon};
					//console.log(i);
					for (var k = 0; k < _all_codons.length; k++) {
						// Compare current codon with other codons
						score[k] = 0;
						
						// Third nucleotide
						if (kmer_map[j].codon[2] != _all_codons[k][2]) {
							score[k] = score[k] + THIRD_NUC_SUB_SCORE;
						}
						// Second nucleotide
						if (kmer_map[j].codon[1] != _all_codons[k][1]) {
							score[k] = score[k] + SECOND_NUC_SUB_SCORE;
						}
						// First nucleotide
						if (kmer_map[j].codon[0] != _all_codons[k][0]) {
							score[k] = score[k] + FIRST_NUC_SUB_SCORE;
						}
						if (score[k] > top_score.score) {
							top_score.score = score[k];
							top_score.position = k;
							top_score.codon = _all_codons[k];
						}
					}
					// Looped through all possible codons; have scores
					// Build new kmer with highest scoring triplets
					new_kmer[counter] = top_score;
					counter++;
				}
				var triplets = new Array();
				var total_score = 0;
				var new_kmer_string = "";
				var old_kmer_string = "";
				
				for (var ii = 0; ii < new_kmer.length;ii++) {
					triplets.push(new_kmer[ii].codon);
					new_kmer_string = new_kmer_string + new_kmer[ii].codon;
					total_score = total_score + new_kmer[ii].score;
				}
				for (var ii = 0; ii < kmer_map.length; ii++) {
					old_kmer_string = old_kmer_string + kmer_map[ii].codon;
				}
				
				// determine melting temperature for the kmer, and filter
				var melting_temp = determineMeltingTemperature(new_kmer_string);
				if (melting_temp < minimum_melting_temp || melting_temp > maximum_melting_temp) {
				  meltingTempCount++;
				  continue;
				}
				
				// determine percentage of sequence changed and filter
				var percent_changed = determinePercentageChanged (new_kmer_string, old_kmer_string);
				if (percent_changed < minimum_recoded) {
				  percentChangedCount++;
				  continue;
				}
				
				var kscore = {
							start_codon:i - (KMER_SIZE / 3),
							start_codon_position:( (i - (KMER_SIZE / 3) ) * 3),
							end_codon: i,
							end_codon_position: (i * 3),
							size:(KMER_SIZE/3),
							codons:triplets,
							score:total_score,
							mt:melting_temp,
							pc:percent_changed
						}
				kmer_scores[kmer_counter] = kscore;
				kmer_counter++;
			}
		
		//i++;
		}
		
		// Check the kmer count
		console.log("KmerCount: " + kmer_counter);
		
		// Have all the filtered kmers
		// need to determine which ones are proper distance apart with highest score
		
		var highest_scores = new Array();
		var _score = 0;
		for (var i = 0; i < kmer_scores.length; i++) {
			for (var j = i; j < kmer_scores.length; j++) {
				if ( i == j )
				  continue;
				var _combined = kmer_scores[i].score + kmer_scores[j].score;
				var _distance = 0;
				var i_left = true;
				if ( kmer_scores[i].start_codon_position < kmer_scores[j].end_codon_position ) {
				  _distance = ( kmer_scores[j].end_codon_position ) - ( kmer_scores[i].start_codon_position );
				} else {
				  //_distance = ( kmer_scores[i].start_codon_position * 3 + KMER_SIZE ) - ( kmer_scores[j].start_codon_position * 3 );
				  _distance = ( kmer_scores[i].end_codon_position ) - ( kmer_scores[j].start_codon_position );
				  i_left = false;
				}
				if (_distance > maximum_amplification) 
				  continue;
				
				if (_combined >= _score && _distance >= minimum_amplification) {
					if (_combined > _score) {
						// Higher score found
						highest_scores.length = 0;
					}
					if (i_left) {
						var _highest = {
							left:kmer_scores[i],
							right:kmer_scores[j],
							distance:_distance
						};
						// start:kmer_scores[j].start_codon_position

					} else {
						var _highest = {
							left:kmer_scores[j],
							right:kmer_scores[i],
							distance:_distance
						};
						// start:kmer_scores[j].start_codon_position
					}
					highest_scores.push(_highest);
				}
			}
		}
		
		for (var j = 0; j < highest_scores.length; j++) {			
			var full_results_html = "<p class=\"nucleotides\">";
			var left_html = "<p class=\"nucleotides\">";
			var newLeftCodonsNoSpace = "";
			
			for (var jj = 0; jj < highest_scores[j].left.codons.length; jj++) {
				if (jj % 3 == 0) {
					if (jj != 0) {
						left_html = left_html + " ";
					}
				}
				left_html = left_html + highest_scores[j].left.codons[jj];
				newLeftCodonsNoSpace = newLeftCodonsNoSpace + highest_scores[j].left.codons[jj];
			}
			left_html = left_html + "</p><p class=\"left results_label\">Pos Start: &nbsp<p class=\"left results_output\"> &nbsp";
			left_html = left_html + highest_scores[j].left.start_codon_position;
			left_html = left_html + "</p><p class=\"left results_label\"> &nbsp| Pos End: &nbsp<p class=\"left results_output\"> &nbsp";
			left_html = left_html + highest_scores[j].left.end_codon_position;
			left_html = left_html + "</p><p class=\"left results_label\"> &nbsp| Score: &nbsp<p class=\"left results_output\"> &nbsp";
			left_html = left_html + highest_scores[j].left.score;
			left_html = left_html + "</p><p class=\"left results_label\"> &nbsp| Temp: &nbsp<p class=\"left results_output\"> &nbsp";
			left_html = left_html + highest_scores[j].left.mt
			left_html = left_html + "</p><p class=\"left results_label\"> &nbsp| Changed: &nbsp<p class=\"left results_output\"> &nbsp";
			left_html = left_html + highest_scores[j].left.pc.toFixed(2)
			left_html = left_html + " %</p>";
			$("#left_watermark").html(left_html);
			
			// Write the nucleotides up to the first watermark and then the left watermark in bold/color			
			var start_pos = highest_scores[j].left.start_codon_position;
			full_results_html = full_results_html + truncated_genomic_sequence.substring(0, start_pos) + "<b style=\"color: blue\">" + newLeftCodonsNoSpace + "</b>";
			
			// Write right watermark			
			var newRightCodonsNoSpace = "";
			var right_html = "<p class=\"nucleotides\">";
			for (var jj = 0; jj < highest_scores[j].right.codons.length; jj++) {
				if (jj % 3 == 0) {
					if (jj != 0) {
						right_html = right_html + " ";
					}
				}
				right_html = right_html + highest_scores[j].right.codons[jj];
				newRightCodonsNoSpace = newRightCodonsNoSpace + highest_scores[j].right.codons[jj];
			}
			
			right_html = right_html + "</p><p class=\"left results_label\">Pos Start: &nbsp<p class=\"left results_output\"> &nbsp";
			right_html = right_html + highest_scores[j].right.start_codon_position;
			right_html = right_html + "</p><p class=\"left results_label\"> &nbsp| Pos End: &nbsp<p class=\"left results_output\"> &nbsp";
			right_html = right_html + highest_scores[j].right.end_codon_position;
			right_html = right_html + "</p><p class=\"left results_label\"> &nbsp| Score: &nbsp<p class=\"left results_output\"> &nbsp";
			right_html = right_html + highest_scores[j].right.score;
			right_html = right_html + "</p><p class=\"left results_label\"> &nbsp| Temp: &nbsp<p class=\"left results_output\">&nbsp";
			right_html = right_html + highest_scores[j].right.mt
			right_html = right_html + "</p><p class=\"left results_label\"> &nbsp| Changed: &nbsp<p class=\"left results_output\">&nbsp";
			right_html = right_html + highest_scores[j].right.pc.toFixed(2)
			right_html = right_html + " %</p>";
			$("#right_watermark").html(right_html);
			
			var _diff = highest_scores[j].right.start_codon_position - highest_scores[j].left.end_codon_position;
			var _final_diff = truncated_genomic_sequence.length - highest_scores[j].right.end_codon_position;
			full_results_html = full_results_html + truncated_genomic_sequence.substring(highest_scores[j].left.end_codon_position,highest_scores[j].left.end_codon_position + _diff) + "<b style=\"color: blue\">" + newRightCodonsNoSpace + "</b>";
			full_results_html = full_results_html + truncated_genomic_sequence.substring(highest_scores[j].right.end_codon_position,truncated_genomic_sequence.length);
						
			$("#full_watermark").html(full_results_html);
			
			console.log("Left: ");
			console.log("\tCodon Start: " + highest_scores[j].left.start_codon);
			console.log("\tPosition Start: " + highest_scores[j].left.start_codon_position);
			console.log("\tCodon End: " + highest_scores[j].left.end_codon);
			console.log("\tPosition End: " + highest_scores[j].left.end_codon_position);
			console.log("\tSize: " + highest_scores[j].left.size);
			console.log("\tTriplets: " + highest_scores[j].left.codons);
			console.log("\tScore: " + highest_scores[j].left.score);
			console.log("\tMelting Point: " + highest_scores[j].left.mt);
			console.log("\tPercent Changed: " + highest_scores[j].left.pc);
			console.log(" ");
			console.log("Right: ");
			console.log("\tCodon Start: " + highest_scores[j].right.start_codon);
			console.log("\tPosition Start: " + highest_scores[j].right.start_codon_position);
			console.log("\tCodon End: " + highest_scores[j].right.end_codon);
			console.log("\tPosition End: " + highest_scores[j].right.end_codon_position);
			console.log("\tSize: " + highest_scores[j].right.size);
			console.log("\tTriplets: " + highest_scores[j].right.codons);
			console.log("\tScore: " + highest_scores[j].right.score);
			console.log("\tMelting Point: " + highest_scores[j].right.mt);
			console.log("\tPercent Changed: " + highest_scores[j].right.pc);
			console.log(" ");
			console.log("Distance: " + highest_scores[j].distance);
			
		}
		
		if (highest_scores.length == 0) {
			// No results
		    
			var no_results_html="<p>No watermarks found within the current parameters.</p>";
			if (meltingTempCount < percentChangedCount) {
				no_results_html = no_results_html + "<p>Mimimum percentage of nucleotides may be set too high for results.</p>";
			} else {
				no_results_html = no_results_html + "<p>Melting temperature range may be set too narrow for results..</p>";
			}
			
			document.getElementById('no_results').innerHTML = no_results_html; 
			document.getElementById('no_results').style.visibility='visible';
		} else {
			// Show tutorial:
			generateTutorial(true, 1);
		}
	} // End of function
	
	
// ----------------------------------------------------------
//
// Support Functions
//
// ----------------------------------------------------------

/*
	function log10(val) {
  		return Math.log(val) / Math.LN10;
	}
*/	


	/**
	 * Determine the meltring temperature for a KMER based on
	 * the different type of nucleotides and using the equation 
	 * from www.basic.northwestern.edu/biotools/oligocalc.html
	 * @author JackFrost2199
	 * @param {string} kmer_string - The string representing the nucleotide sequence that should be used to generate a melting temperature.
	 * 
	 */
	function determineMeltingTemperature (kmer_string) {
		var wA = kmer_string.split("A").length - 1;
		var zC = kmer_string.split("C").length - 1;
		var yG = kmer_string.split("G").length - 1;
		var xT = kmer_string.split("T").length - 1;
		
		var Tm = 0;
		
		// Using equation from www.basic.northwestern.edu/biotools/oligocalc.html		

		if (kmer_string > 13) {
			Tm = 64.9 + 41 * (yG + zC - 16.4) / (wA + xT + yG + zC);
		} else {
			Tm = (wA + xT) * 2 + (yG + zC) * 4;
		}
	
		return (Tm);
	}
	
	function determinePercentageChanged (new_kmer, old_kmer) {
		if (new_kmer.length != old_kmer.length) {
			console.log("DEVELOPER: new kmer length does not match old kmer length");
			return 0;
		}
		
		// determine percentage difference here
		var match = 0;
		var mismatch = 0;
		var total = old_kmer.length;
		
		for (var i = 0; i < old_kmer.length; i++) {
			if (old_kmer[i] == new_kmer[i]) match++;
			else mismatch++;
		}
		
		var variation_percentage = mismatch / old_kmer.length * 100;
		return variation_percentage;
	}
	
// ----------------------------------------------------------
//
// VALIDATIONS
//
// ----------------------------------------------------------
	function validateAll () {
		// Validate all blocks; generate any errors
		var _valid = true;
		var failed = false;
		var submitted = true;
		var error_id;
	
		// Make sure minimum melting temperature is a valid number in a valid range
		error_id = "#minimum_melting_temp";
		_valid = validateMeltingTemperature (submitted, error_id);
		if (!_valid) failed = true;

		// Make sure maximum melting temperature is a valid number in a valid range
		error_id = "#maximum_melting_temp";
		_valid = validateMeltingTemperature (submitted, error_id);
		if (!_valid) failed = true;
	
		// Make sure the melting temperature range is valid
		error_id = ["#minimum_melting_temp", "#maximum_melting_temp"];
		_valid = validateMeltingTemperatureRanges (submitted, error_id);
		if (!_valid) failed = true;
	
		error_id = "#minimum_recoded";
		_valid = validateMinimumPercentageRecoded (submitted, error_id);
		if (!_valid) failed = true;

		error_id = "#minimum_amplification";
		_valid = validateAmplificationRegion (submitted, error_id);
		if (!_valid) failed = true;
	
		error_id = "#maximum_amplification";
		_valid = validateAmplificationRegion (submitted, error_id);
		if (!_valid) failed = true;
		
		error_id = ["#minimum_amplification","#maximum_amplification"];
		_valid = validateAmplificationRange (submitted, error_id);
		if (!_valid) failed = true;
		
		error_id = "#genomic_sequence";
		_valid = validateGenomeSequence (submitted, error_id);
		if (!_valid) failed = true; 

		error_id = ["#genomic_sequence", "#minimum_amplification"];
		_valid = validateGenomeLength (submitted, error_id);
		if (!_valid) failed = true;
		
		return failed;
	}

/**
 * Generically set properties of error messages based on the input
 * @author JackFrost2199
 * @param {Bool} submitted - Whether or not the computation has been submittted
 * @param {String} error_id - The DIV id that the error message should be placed in
 * 
 */
function setErrors (submitted, error_id) {
	if (submitted) $( "#error_alert" ).css("display", "block");
	if ($.isArray(error_id)){
		for (var i = 0; i < error_id.length; i++) {
			$( error_id[i] + "_error" ).css("display", "block");
			$( error_id[i] + "_label" ).addClass("error");
		}	
	} else {
		$( error_id + "_error" ).css("display", "block");
		$( error_id + "_label" ).addClass("error");
	}
}

/**
 * Determine if the temperature predicted is between the MIN_TEMP and the MAX_TEMP and is a number
 * @author JackFrost2199
 * @param {Bool} submitted - Whether or not the computation has been submittted
 * @param {String} error_id - The DIV id that the error message should be placed in
 * @returns {Bool} True if passes validation, false if it fails
 */
function validateMeltingTemperature (submitted, error_id) {
	//var _minimum_melting_temp = document.getElementById("minimum_melting_temp").value;
	var _melting_temp = $( error_id ).val();
	if ( isNaN(_melting_temp) ) {
		$( error_id + "_error" ).text("Temperature must be a number.");
	} else if ( _melting_temp < MIN_TEMP || _melting_temp > MAX_TEMP ) {
		$( error_id + "_error" ).text("Value must be a number between " + MIN_TEMP + " and " + MAX_TEMP + " .");
	} else return true; // Meets all requirements so return true
	
	// Set all appropriate error flags
	setErrors (submitted, error_id);
	return false;
}

/**
 * Validate that the melting temperatures are appropriately spaced (ie. minimum is not larger than maximum)
 * @author JackFrost2199
 * @param {Bool} submitted - Wheter or not the computation has been submitted
 * @param {String} error_id - The DIV id that the error message should be placed in
 * @returns {Bool} True if passes validation, false if it fails
 */
function validateMeltingTemperatureRanges (submitted, error_id) {
	var _min_temp = $( error_id[0] ).val();
	var _max_temp = $( error_id[1] ).val();
	if (_min_temp > _max_temp) {
		$( error_id[0] + "_error" ).text("Value must be less than or equal to maximum temperature.");
		$( error_id[1] + "_error" ).text("Value must be greater than or equal to minimum temperature.");
	} else return true;

	// Set all appropriate error flags
	setErrors (submitted, error_id);
	return false;
}

/**
 * Validate the the minimum percentage of recoded required is between 0 and 100
 * @author JackFrost2199
 * @param {Bool} submitted - Wheter or not the computation has been submitted
 * @param {String} error_id - The DIV id that the error message should be placed in
 * @returns {Bool} True if passes validation, false if it fails
 */
function validateMinimumPercentageRecoded (submitted, error_id) {
	var _minimum_recoded = $(error_id).val();
	if ( isNaN(_minimum_recoded) ) {
		$( error_id + "_error" ).text("Percentage must be a number.")
	} else if (_minimum_recoded < MIN_PERCENT || _minimum_recoded > MAX_PERCENT) {
		$( error_id + "_error" ).text("Percentage must be between " + MIN_PERCENT + "% and " + MAX_PERCENT + "%.")
	} else return true;
	
	// Set all appropriate error flags
	setErrors (submitted, error_id);
	return false;
}

/**
 * Make sure amplification values are valid (is a number and is between the hard Minimum and Maximum
 * amplification sizes.
 * @author JackFrost2199
 * @param {Bool} submitted - Wheter or not the computation has been submitted
 * @param {String} error_id - The DIV id that the error message should be placed in
 * @returns {Bool} True if passes validation, false if it fails
 */
function validateAmplificationRegion (submitted, error_id) {
	var _amplification = $( error_id ).val();
	if ( isNaN(_amplification) ) {
		$( error_id + "_error" ).text("Region size must be a number.")
	} else if (_amplification < MIN_AMP) {
		$( error_id + "_error" ).text("Region size must be at least " + MIN_AMP + " nucleotides.")
	} else if (_amplification > MAX_AMP) {
		$( error_id + "_error" ).text("Region size must be no larger than " + MAX_AMP + " nucleotides.")
	} else return true;
	
	// Set all appropriate error flags
	setErrors (submitted, error_id);
	return false;
}

/**
 * Make sure amplification size range is a positive number
 * @author JackFrost2199
 * @param {Bool} submitted - Wheter or not the computation has been submitted
 * @param {String} error_id - The DIV id that the error message should be placed in
 * @returns {Bool} True if passes validation, false if it fails
 */
function validateAmplificationRange (submitted, error_id) {
	var _min_amp = $( error_id[0] ).val();
	var _max_amp = $( error_id[1] ).val();
	if (_min_amp > _max_amp) {
		$( error_id[0] + "_error" ).text("Value must be less than or equal to largest amplification region.");
		$( error_id[1] + "_error" ).text("Value must be greater than or equal to smallest amplification region.");
	} else return true;

	// Set all appropriate error flags
	setErrors (submitted, error_id);
	return false;
}

/**
 * Validate that the genomic information is valid
 * @author JackFrost2199
 * @param {Bool} submitted - Wheter or not the computation has been submitted
 * @param {String} error_id - The DIV id that the error message should be placed in
 * @returns {Bool} True if passes validation, false if it fails
 */
function validateGenomeSequence (submitted, error_id) {
	var _sequence = $( error_id ).val().toLowerCase();
	_sequence = _sequence.replace(/(\r\n|\n|\r|\s+)/gm,"");

	//DEBUG
	//var dbg = _sequence.split("\n");
	//console.log("Number of newlines: " + dbg.length);
		
	var passed = true;
	for (var i = 0; i < _sequence.length; i++) {
		var invalid = true;
		for (var j = 0; j < NUCLEOTIDES.length; j++) {
			if (_sequence[i] == NUCLEOTIDES[j]) {
				invalid = false;
				break;
			}
		}
		if (invalid) {
			// Set error; there is an unsupported nucleotide
			passed = false;
			break;
		}
	}
	if (passed) return true; // No need to set errors
	
	// Print out nucleotides allowed
	var _nuc_error = "";
	for (var i = 0; i < NUCLEOTIDES.length; i++) {
		_nuc_error = _nuc_error + NUCLEOTIDES[i] + ",";
	}
	_nuc_error = _nuc_error.slice(0, -1);
	
	$( error_id + "_error" ).text("Only nucleotides " + _nuc_error.toUpperCase() + ".");
	
	setErrors (submitted, error_id);
	return false;
}

/**
 * Validate Genome Length.  Determine if sequence length is too small for the minimum amplification
 * @author JackFrost2199
 * @param {Bool} submitted - Wheter or not the computation has been submitted
 * @param {String} error_id - The DIV id that the error message should be placed in
 * @returns {Bool} True if passes validation, false if it fails
 * 
 */
function validateGenomeLength (submitted, error_id) {
	var _sequence = $( error_id[0] ).val().toLowerCase();
	var _min_amp = $( error_id[1] ).val();
	//if (_sequence.length < (GENE_BEGINING + GENE_END + parseInt(_min_amp) + 50) ) {
	if (_sequence.length < (parseInt(_min_amp)) ) {
		// Sequence length is too small for the minimum amplification
		
		$( error_id[0] + "_error" ).text("Too few nucleotides in gene sequence.  Must be at least the size of the minimum amplification.");
		setErrors(submitted, error_id[0]);
		return false;
	}
	return true;
}

/**
 * Set the codon table based on the organism.
 *@param {string} organism - This is the organims that the codon table should be generated based off of
 * 
 */
function setCodonTable (organism) {
  if (organism == "mycobacterium") {
	// Mycobacterium smegmatis str. MC2 155 amino acid table
	AA_TABLE = {
		A:["GCT","GCC","GCA","GCG"],
		R:["AGA","AGG","CGT","CGC","CGA","CGG"],
		N:["AAT","AAC"],
		D:["GAT","GAC"],
		C:["TGT","TGC"],
		Q:["CAA","CAG"],
		E:["GAA","GAG"],
		G:["GGT","GGA","GGC","GGG"],
		H:["CAT","CAC"],
		I:["ATT","ATC","ATA"],
		L:["TTA","TTG","CTT","CTC","CTA","CTG"],
		K:["AAA","AAG"],
		M:["ATG"],
		F:["TTT","TTC"],
		P:["CCT","CCC","CCA","CCG"],
		S:["AGT","AGC"],
		T:["ACT","ACC","ACA","ACG"],
		W:["TGG"],
		Y:["TAT","TAC"],
		V:["GTT","GTC","GTA","GTG"],
		STOP:["TAA","TAG","TGA"]
	};

	// Mycobacterium smegmatis str. MC2 155 codon table
	CODON_TABLE = {
		AAA:"K",AAC:"N",AAG:"K",AAT:"N",TTT:"F",TTC:"F",TTA:"L",TTG:"L",CTT:"L",CTC:"L",CTA:"L",CTG:"L",
		ATT:"I",ATC:"I",ATA:"I",ATG:"M",GTT:"V",GTC:"V",GTA:"V",GTG:"V",TCT:"S",TCC:"S",TCA:"S",TCG:"S",
		CCT:"P",CCC:"P",CCA:"P",CCG:"P",ACT:"T",ACC:"T",ACA:"T",ACG:"T",GCT:"A",GCC:"A",GCA:"A",GCG:"A",
		TAT:"Y",TAC:"Y",TAA:"STOP",TAG:"STOP",CAT:"H",CAC:"H",CAA:"Q",CAG:"Q",GAT:"D",GAC:"D",GAA:"E",GAG:"E",
		TGT:"C",TGC:"C",TGA:"STOP",TGG:"W",CGT:"R",CGC:"R",CGA:"R",CGG:"R",AGT:"S",AGC:"S",AGA:"R",AGG:"R",
		GGT:"G",GGC:"G",GGA:"G",GGG:"G"
	};
  } else {
	// Standard codon table is loaded by default already
	return;
  }
}

/**
 * Generate the tutorial for use in Watermarker.
 * This gives three walk through steps of the process
 * so users can learn.  Recursive function that generates the tutorial hovers.
 * @param {bool} tutorial_needed - Toggle whether or not the tutorial should be shown
 * @param {int} tutorial_index - The index for whichever tutorial needs to be pushed out.
 * 
 */
function generateTutorial (tutorial_needed, tutorial_index) {
  if(!tutorial_needed) 
	return;
  
  var tutorialHTML;
  switch(tutorial_index) {
	case 1:
	  tutorialHTML="<p><div class=\"center\"><img src=\"img/first_header.png\" class=\"tutorial_header\"></div><div style=\"display:table;\"><div style=\"float:right;\"><img src=\"img/dna_small.png\" height=\"211\" width=\"100\"></img></div><div class=\"tutorial_title\"><br>Minimum and maximum melting temperature</div><div  class=\"tutorial_text\">DNA is a double stranded molecule that forms a double helix chape in its natural condition.  At a certain temperature a DNA doublle helix will unwind or 'melt.'  The temperature required for this depends in large part on the nucleotide pairing within the double helix, with C-G pairings requiring more energy (and therefore a higher tempurature) to 'melt' than A-T pairs.<br><br><button onclick=\"generateTutorial(true, 2)\">Next</button></div></div></p>"
	  break;
	case 2:
	  tutorialHTML="<p><div class=\"center\"><img src=\"img/second_header.png\" class=\"tutorial_header\"></div></div><div style=\"display:table;\"><div style=\"float:right;\"><img src=\"img/Codons_aminoacids_table_small.png\" height=\"211\" width=\"100\"></img></div><div class=\"tutorial_title\">Minimum percentage of recoded nucleotides</div><div class=\"tutorial_text\">This parameter is the minimum change in nucleotids that you are requiring for your watermarks.  The purpose of recoding nuclotides during the watermarking phase is to insert stretches of DNA into the synthetic gene or genome that does not change any function (they code for the same amino acids and therefore the same proteins) but offers a target for you to examine to make sure you are working with your synthetic gene.<br><br><button onclick=\"generateTutorial(true, 3)\">Next</button></div></div></div></p>"
	  break;
	case 3:
	  tutorialHTML="<p><div><img src=\"img/third_header.png\" class=\"tutorial_header\"></img></div><div class=\"tutorial_title\">Smallest to largest amplification region allowed</div><div class=\"tutorial_text\">This parameter sets the range of the size that the amplification region flanked by the watermarks can be.  This includes the watermarks themselves.  Typically this is between 200 and 500 which is a large enough range to amplify successfully in PCR without being too large.  This can vary depending on the size of your gene or genome that you wish to watermark.<div class=\"next_button\"><br /><button onclick=\"generateTutorial(true, 4)\">Next</button></div></div></p>"
	  break;
	default:
	  // remove DIVs
	  document.getElementById('light').style.visibility='hidden';
	  document.getElementById('fade').style.visibility='hidden';
	  document.getElementById('results_section').style.visibility='visible';
	  return;
  }
  
  // Change the lightbox HTML
  document.getElementById('light').innerHTML=tutorialHTML;
  
  // Show the dark faded background and the lightbox
  document.getElementById('light').style.display='block';
  document.getElementById('fade').style.display='block';
  document.getElementById('light').style.visibility='visible';
  document.getElementById('fade').style.visibility='visible';
}

//
// Generate Oops message if parameters appear to strict
//

function generateOops (oops_needed) {
	if(!oops_needed)
	  return;
	
	
}