<?php

require_once 'lib/limonade.php';
require_once 'lib/models.php';
require_once 'lib/util.php';

function configure() {
    ORM::configure('sqlite:/var/local/sample_registry/core.db');
}

function before() {
    layout('layout_default.html.php');
    option('base_uri', '/registry');
}


##########################################
## Tags
##########################################

dispatch('/tags', 'show_tags');
function show_tags() {
    $tags = query_tags();
    $maxcnt = 0;
    foreach ($tags as $t) {
        if ($t->key_counts > $maxcnt) {
            $maxcnt = $t->key_counts;
        }
    }
    set('tags', $tags);
    set('maxcnt', $maxcnt);
    return html('browse_tags.html.php');
}

function get_standard_tags() {
    return array(
        'SampleType' => 'sample_type',
        'HostSpecies' => 'host_species',
        'SubjectID' => 'subject_id');
}

dispatch('/tags/:tag', 'show_tag');
function show_tag() {
    $tag = params('tag');
    $standard_tags = get_standard_tags();
    if (array_key_exists($tag, $standard_tags)) {
        $stats = query_standard_tag_stats($standard_tags[$tag]);
    } else {
        $stats = query_tag_stats($tag);
    }
    set('tag', $tag);
    set('stats', $stats);
    return html('show_tag.html.php');
}

dispatch('/tags/:tag/:value', 'show_tag_value');
function show_tag_value() {
    $tag = params('tag');
    $val = params('value');
    $standard_tags = get_standard_tags();
    if (array_key_exists($tag, $standard_tags)) {
        $samples = query_standard_tag_value($standard_tags[$tag], $val);
    } else {
        $annotations = query_tag_value($tag, $val);
        $sample_accessions = array();
        foreach ($annotations as $a) {
            $sample_accessions[] = $a->sample_accession;
        }
        $samples = query_samples_list($sample_accessions);
    }
    $sample_metadata = query_multisample_annotations($samples);
    $keyed_metadata = key_by_attribute($sample_metadata, "sample_accession");
    set('tag', $tag);
    set('value', $val);
    set('samples', $samples);
    set('sample_metadata', $keyed_metadata);
    return html('show_tag_value.html.php');
}


########################################
## Stats
########################################
dispatch('/stats', 'show_stats');
function show_stats() {
    set('num_samples', query_total_samples());

    set('num_samples_with_sampletype', query_total_sampletypes());
    set('num_samples_with_standard_sampletype', query_total_standard_sampletypes());
    set('standard_sampletype_counts', query_standard_sampletype_counts());
    set('nonstandard_sampletype_counts', query_nonstandard_sampletype_counts());

    set('num_subjectid', query_num_subjectid());
    set('num_subjectid_with_hostspecies', query_num_subjectid_with_hostspecies());

    set('num_samples_with_hostspecies', query_total_hostspecies());
    set('num_samples_with_standard_hostspecies', query_total_standard_hostspecies());
    set('standard_hostspecies_counts', query_standard_hostspecies_counts());
    set('nonstandard_hostspecies_counts', query_nonstandard_hostspecies_counts());

    set('num_samples_with_primer', query_num_primer());
    set('num_samples_with_reverse_primer', query_num_reverse_primer());

    return html('show_stats.html.php');
}


########################################
## Runs
########################################

dispatch('/', 'show_runs');
dispatch('/runs', 'show_runs');
function show_runs() {
    $runs = query_runs();
    set('runs', $runs);
    return html('browse_runs.html.php');
}

dispatch('^/runs/(\d+)', 'show_run');
function show_run() {
    $run_accession = params(0);
    $run = query_run($run_accession);
    if (!$run) {
        halt(NOT_FOUND, "Run $run_accession does not exist.");
    }
    $samples = query_run_samples($run_accession);
    $sample_metadata = query_multisample_annotations($samples);
    $keyed_metadata = key_by_attribute(
        $sample_metadata, "sample_accession");
    set('run', $run);
    set('samples', $samples);
    set('sample_metadata', $keyed_metadata);
    return html('show_run_samples.html.php');
}

dispatch('^/runs/(\d+).txt', 'export_samples_for_qiime');
function export_samples_for_qiime() {
    $run_accession = params(0);
    $run = query_run($run_accession);
    if (!$run) {
        halt(NOT_FOUND, "Run $run_accession does not exist.");
    }
    $samples = query_run_samples($run_accession);
    $sample_metadata = query_multisample_annotations($samples);

    # Change ReversePrimerSequence for compatibility with QIIME
    foreach ($sample_metadata as $a) {
        if ($a->key == "ReversePrimerSequence") {
            $a->key = "ReversePrimer";
        }
    }

    list($cols, $table) = cast_annotations($sample_metadata, $samples);
    set('run', $run);
    set('samples', $samples);
    set('metadata', $table);
    set('metadata_columns', $cols);
    return txt('export_qiime.txt.php', null);
}

dispatch('^/runs/(\d+).tsv', 'export_samples_tab_delim');
function export_samples_tab_delim() {
    $run_accession = params(0);
    $run = query_run($run_accession);
    if (!$run) {
        halt(NOT_FOUND, "Run $run_accession does not exist.");
    }
    $samples = query_run_samples($run_accession);
    $sample_metadata = query_multisample_annotations($samples);
    list($cols, $table) = cast_annotations($sample_metadata, $samples);
    set('run', $run);
    set('samples', $samples);
    set('metadata', $table);
    set('metadata_columns', $cols);
    return txt('export_delim.txt.php', null);
}


########################################
## Samples
########################################

dispatch('^/samples/(\d+).json', 'export_sample_as_json');
function export_sample_as_json() {
    $sample_accession = params(0);
    $sample = query_sample($sample_accession);
    if (!$sample) {
        halt(NOT_FOUND, "Sample $sample_accession does not exist.");
    }
    $annotations = query_sample_annotations($sample_accession);

    $vals = $sample->as_array();
    foreach ($annotations as $a) {
        $vals[$a->key] = $a->val;
    }

    return json($vals, null);
}

dispatch('^/samples/startingwith/([\w\.\-\_]+)', 'match_samples');
function match_samples() {
    $name = params(0);
    $samples = query_sample_match($name);
    $sample_metadata = query_multisample_annotations($samples);
    $keyed_metadata = key_by_attributes(
        $sample_metadata, array("sample_accession", "filepath"));
    set('match', $name);
    set('samples', $samples);
    set('sample_metadata', $keyed_metadata);
    return html('show_samples_list.html.php');
}

run();
