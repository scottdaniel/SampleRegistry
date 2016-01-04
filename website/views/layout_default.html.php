<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" 
   "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <link rel="stylesheet" href="<?= url_for('css', 'blueprint', 'screen.css'); ?>" type="text/css" media="screen, projection">
    <link rel="stylesheet" href="<?= url_for('css', 'blueprint', 'print.css'); ?>" type="text/css" media="print">
    <!--[if lt IE 8]>
    <link rel="stylesheet" href="<?= url_for('css', 'blueprint', 'ie.css'); ?>" type="text/css" media="screen, projection">
    <![endif]-->
    <link rel="stylesheet" href="<?= url_for('css', 'custom.css'); ?>" type="text/css">

    <script type="text/javascript" language="javascript" src="<?= url_for('js', 'jquery.js'); ?>"></script>
    <script type="text/javascript" language="javascript" src="<?= url_for('js', 'jquery.dataTables.min.js'); ?>"></script>
    <title>Sample registry</title>
  </head>

  <body>
    <div class="container">
      <div class="header span-16">
	    <h1><a href="<?= url_for() ?>">CHOP Microbiome Center sample registry</a></h1>
	    <ul>
          <li><a href="<?= url_for('runs') ?>">Runs</a></li>
          <li><a href="<?= url_for('tags') ?>">Metadata</a></li>
        </ul>
	  </div>
	  <div class="logoarea span-8 last">
	    <img class="sitelogo" src="<?= url_for('img', 'ricks_dna.png') ?>" />
      </div>
	  <div class="span-24 last">
	    <?= $content; ?>
      </div>
    </div>
  </body>
</html>
