<p>Every sample should have a SampleType: <?= $num_samples_with_sampletype ?> of <?= $num_samples ?> (<?= sprintf("%.2f", 100 * $num_samples_with_sampletype / $num_samples) ?>%).</p>

<p>All SampleType values should be in the approved list: <?= $num_samples_with_standard_sampletype ?> of <?= $num_samples_with_sampletype ?> (<?= sprintf("%.2f", 100 * $num_samples_with_standard_sampletype / $num_samples_with_sampletype) ?>%).</p>

Standard sample types:
<table>
<tr><th>SampleType</th><th>Count</th></tr>
<?php
foreach ($standard_sampletype_counts as $s) {
?>
<tr><td><?= $s->sample_type ?></td><td><?= $s->num_samples ?></td></tr>
<?php
 }
?>
</table>

Nonstandard sample types:
<table>
<tr><th>SampleType</th><th>Count</th></tr>
<?php 
foreach ($nonstandard_sampletype_counts as $s) {
?>
<tr><td><?= $s->sample_type ?></td><td><?= $s->num_samples ?></td></tr>
<?php
}
?>
</table>

<p>If SubjectID tag is filled in, HostSpecies tag should also be filled in: <?= $num_subjectid_with_hostspecies ?> of <?= $num_subjectid ?> (<?= sprintf("%.2f", 100 * $num_subjectid_with_hostspecies / $num_subjectid) ?>%).</p>

     <p>All HostSpecies values should be in the approved list: <?= $num_samples_with_standard_hostspecies ?> of <?= $num_samples_with_hostspecies ?> (<?= sprintf("%.2f", 100 * $num_samples_with_standard_hostspecies / $num_samples_with_hostspecies) ?>%).</p>

Standard host species:
<table>
<tr><th>HostSpecies</th><th>Count</th></tr>
<?php
foreach ($standard_hostspecies_counts as $s) {
?>
<tr><td><?= $s->host_species ?></td><td><?= $s->num_samples ?></td></tr>
<?php
}
?>
</table>

Nonstandard host species:
<table>
<tr><th>HostSpecies</th><th>Count</th></tr>
<?php
foreach ($nonstandard_hostspecies_counts as $s) {
?>
<tr><td><?= $s->host_species ?></td><td><?= $s->num_samples ?></td></tr>
<?php
}
?>
</table>
