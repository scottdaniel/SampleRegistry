#SampleID	BarcodeSequence	LinkerPrimerSequence	SampleType	HostSpecies	SubjectID	<?php if ($metadata_columns) { echo implode("\t", $metadata_columns), "\t"; } ?>Description
<?php

$comment = str_replace(array("\n", "\r"), "", $run->comment);

echo "#$comment\n";
echo "#Sequencing date: $run->run_date\n";
echo "#File name: " . basename($run->data_uri) . "\n";
echo "#Lane: $run->lane\n";
echo "#Platform: $run->machine_type $run->machine_kit\n";
echo "#Run accession: " . format_run_accession($run->run_accession) . "\n";

foreach ($samples as $sample) {
    $head_vals = array(
        $sample->sample_name,
        strtoupper($sample->barcode_sequence),
        strtoupper($sample->primer_sequence),
        $sample->sample_type ? $sample->sample_type : "NA",
        $sample->host_species ? $sample->host_species : "NA",
        $sample->subject_id ? $sample->subject_id : "NA");
    echo implode("\t", $head_vals), "\t";

    if ($metadata_columns) {
        echo implode("\t", $metadata[$sample->sample_accession]), "\t";
    }

    $tail_vals = array(
        format_sample_accession($sample->sample_accession), 
        );
    echo implode("\t", $tail_vals), "\n";
}

?>