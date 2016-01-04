<?php

/*
 * Format dates for display
 */
function format_date($date_str) {
    $d = explode("-", $date_str);
    return implode("/", array($d[1], $d[2], $d[0]));
}

function format_sample_accession($n) {
    return sprintf("PCMP%06d", $n);
}

function format_run_accession($n) {
    return sprintf("PCMP%06d", $n);
}

function cast_annotations($annotations, $samples, $default = "NA") {
    $cols = array();
    $table = array();
    foreach ($samples as $s) {
        $table[$s->sample_accession] = array();
    }

    foreach ($annotations as $a) {
        if (!isset($cols[$a->key])) {
            // Add new column to each row of table
            foreach (array_keys($table) as $r) {
                $table[$r][$a->key] = $default;
            }
            // Add new column to future rows
            $cols[$a->key] = $default;            
        }
        $table[$a->sample_accession][$a->key] = $a->val;
    }
    return array(array_keys($cols), $table);
}


/*
 * Get a value from an array, or return default value.
 */
function array_get($arr, $key, $default, $allow_null = FALSE) {
    if ($allow_null) {
        $key_exists = array_key_exists($key, $arr);
    } else {
        $key_exists = isset($arr[$key]);
    }
    if ($key_exists) {
        return $arr[$key];
    }
    return $default;
}

/**
 * Create an array of objects, using the values of an attribute as keys.
 *
 * Since multiple objects may share the same value for an attribute,
 * each key points to an array of objects.
 *
 */
function key_by_attribute($objs, $attr_name) {
    $keyed_objs = array();
    foreach ($objs as $obj) {
        $key = $obj->$attr_name;
        if (!array_key_exists($key, $keyed_objs)) {
            $keyed_objs[$key] = array();
        }
        $keyed_objs[$key][] = $obj;
    }
    return $keyed_objs;
}

/**
 * Recursively apply key_by_attribute over multiple attributes.
 *
 * Returns a nested array of objects.
 */
function key_by_attributes($objs, $attr_names) {
    $attr_name = array_shift($attr_names);
    $keyed_objs = key_by_attribute($objs, $attr_name);
    if ($attr_names) {
        foreach($keyed_objs as $key => $kobjs) {
            $keyed_objs[$key] = key_by_attributes($kobjs, $attr_names);
        }
    }
    return $keyed_objs;
}

