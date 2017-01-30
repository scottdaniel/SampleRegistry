<?php

require_once 'idiorm.php';

/* Run */

function query_runs() {
    return ORM::for_table('runs_samplecounts')
        ->find_many();
}

function query_run($run_accession) {
    return ORM::for_table('runs')
        ->where_equal('run_accession', $run_accession)
        ->find_one();
}

/* Sample */

function query_sample($sample_accession) {
    return ORM::for_table('runs_samples')
        ->where_equal('sample_accession', $sample_accession)
        ->find_one();
}

function query_run_samples($run_accession) {
    return ORM::for_table('samples')
        ->where_equal('samples.run_accession', $run_accession)
        ->order_by_asc('sample_name')
        ->order_by_asc('sample_accession')
        ->find_many();
}

function query_samples_list($sample_accessions) {
    if (!$sample_accessions) {
        return array();
    }
    return ORM::for_table('runs_samples')
        ->where_in('sample_accession', $sample_accessions)
        ->find_many();
}

function query_sample_match($partial_name) {
    return ORM::for_table('runs_samples')
        ->where_like('sample_name', $partial_name . "%")
        ->find_many();
}

/* Metadata */

function query_multisample_annotations($samples) {
    if (!$samples) {
        return array();
    }
    $sample_accessions = array();
    foreach($samples as $s) {
        $sample_accessions[] = $s->sample_accession;
    }

    # Process in 500 sample chunks for SQLite
    # SQLITE_MAX_VARIABLE_NUMBER is set to 999
    $chunk_size = 500;
    $num_samples = count($sample_accessions);
    $metadata = array();
    $offset = 0;
    while ($offset < $num_samples) {
        $chunk_accessions = array_slice($sample_accessions, $offset, $chunk_size);
        $chunk_metadata = ORM::for_table('annotations')
            ->where_in('sample_accession', $chunk_accessions)
            ->find_many();
        $metadata = array_merge($metadata, $chunk_metadata);
        $offset = $offset + $chunk_size;
    }

    return $metadata;
}

function query_multisample_annotations_impl($sample_accessions) {
    $metadata = ORM::for_table('annotations')
        ->where_in('sample_accession', $sample_accessions)
        ->find_many();
    return $metadata;
}

function query_sample_annotations($sample_accession) {
    return ORM::for_table('annotations')
        ->where_in('sample_accession', $sample_accession)
        ->find_many();
}

function query_tag_stats($tag) {
    return ORM::for_table('annotation_vals_by_run')
        ->where_equal('key', $tag)
        ->find_many();
}

function query_standard_tag_stats($tag) {
    return ORM::for_table('samples')
        ->select_many_expr(array(
            'val' => $tag, 
            'sample_count' => 'COUNT(samples.sample_accession)', 
            'run_accession' => 'runs.run_accession',
            'run_date' => 'runs.run_date',
            'run_comment' => 'runs.comment'))
        ->join('runs', array('samples.run_accession', '=', 'runs.run_accession'))
        ->group_by($tag)->group_by('samples.run_accession')
        ->where_not_null($tag)
        ->find_many();
}

function query_tag_value($tag, $value) {
    return ORM::for_table('annotations')
        ->where_equal('key', $tag)
        ->where_equal('val', $value)
        ->find_many();
}

function query_standard_tag_value($tag, $value) {
    return ORM::for_table('samples')
        ->join('runs', array('samples.run_accession', '=', 'runs.run_accession'))
        ->where_equal($tag, $value)
        ->find_many();
}

function query_tags() {
    return ORM::for_table('annotation_keys')
        ->find_many();
}

/* Stats */

function query_total_samples() {
    return ORM::for_table('samples')->count();
}

function query_total_sampletypes() {
    return ORM::for_table('samples')
        ->where_not_null('sample_type')
        ->count();
}

function query_total_standard_sampletypes() {
    return ORM::for_table('samples')
        ->join('standard_sample_types', array(
            'samples.sample_type', '=', 'standard_sample_types.sample_type'))
        ->count();
}

function query_standard_sampletype_counts() {
    return ORM::for_table('standard_sample_types')
        ->select_many_expr(array(
            'sample_type' => 'standard_sample_types.sample_type',
            'num_samples' => 'COUNT(samples.sample_accession)',
            'host_associated' => 'standard_sample_types.host_associated'))
        ->left_outer_join('samples', array(
            'standard_sample_types.sample_type', '=', 'samples.sample_type'))
        ->group_by('standard_sample_types.sample_type')
        ->order_by_desc('num_samples')
        ->find_many();
}

function query_nonstandard_sampletype_counts() {
    return ORM::for_table('samples')
        ->select_many_expr(array(
            'sample_type' => 'samples.sample_type',
            'num_samples' => 'COUNT(samples.sample_accession)'))
        ->left_outer_join('standard_sample_types', array(
            'samples.sample_type', '=', 'standard_sample_types.sample_type'))
	->where_null('standard_sample_types.sample_type')
        ->group_by('samples.sample_type')
        ->order_by_desc('num_samples')
        ->find_many();
}

function query_num_subjectid() {
    return ORM::for_table('samples')->where_not_null('subject_id')->count();
}

function query_num_subjectid_with_hostspecies() {
    return ORM::for_table('samples')
        ->where_not_null('subject_id')
        ->where_not_null('host_species')
        ->count();
}

function query_total_hostspecies() {
    return ORM::for_table('samples')->where_not_null('host_species')->count();
}

function query_total_standard_hostspecies() {
    return ORM::for_table('samples')
        ->join('standard_host_species', array(
            'samples.host_species', '=', 'standard_host_species.host_species'))
        ->count();
}

function query_standard_hostspecies_counts() {
    return ORM::for_table('standard_host_species')
        ->select_many_expr(array(
            'host_species' => 'standard_host_species.host_species',
            'num_samples' => 'COUNT(samples.sample_accession)',
            'ncbi_taxon_id' => 'standard_host_species.ncbi_taxon_id'))
        ->left_outer_join('samples', array(
            'standard_host_species.host_species', '=', 'samples.host_species'))
        ->group_by('standard_host_species.host_species')
        ->order_by_desc('num_samples')
        ->find_many();
}

function query_nonstandard_hostspecies_counts() {
    return ORM::for_table('samples')
        ->select_many_expr(array(
            'host_species' => 'samples.host_species',
            'num_samples' => 'COUNT(samples.sample_accession)'))
        ->left_outer_join('standard_host_species', array(
            'samples.host_species', '=', 'standard_host_species.host_species'))
        ->where_null('standard_host_species.host_species')
        ->where_not_null('samples.host_species')
        ->group_by('samples.host_species')
        ->order_by_desc('num_samples')
        ->find_many();
}

function query_num_primer() {
    return ORM::for_table('samples')
        ->where_not_equal('primer_sequence', '')
        ->count();
}

function query_num_reverse_primer() {
    return ORM::for_table('annotations')
        ->distinct()
        ->select('sample_accession')
        ->where('key', 'ReversePrimerSequence')
        ->count();
}
