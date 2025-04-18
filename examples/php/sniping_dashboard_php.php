<?php
require 'vendor/autoload.php';
use SolanaMVP\SnipingDashboard;
use SolanaMVP\Dex\Jupiter;

$dashboard = new SnipingDashboard(new Jupiter());
$data = $dashboard->getLatestSnipes();
foreach ($data as $snipe) {
    echo "{$snipe->pair} at {$snipe->price}\n";
}
?>