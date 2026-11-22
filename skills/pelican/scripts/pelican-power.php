<?php
// Power actions through Pelican's own Wings client, the same path as the panel's
// power buttons. Going through the panel (not docker) matters: wings has
// crash_detection.detect_clean_exit_as_crash=true, so stopping a game server any
// other way is recorded as a crash.
//   pelican-power.php <server-id> start|stop|restart|status
require '/var/www/pelican/vendor/autoload.php';
$app = require '/var/www/pelican/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

$id     = (int) ($argv[1] ?? 0);
$action = $argv[2] ?? 'status';

$server = App\Models\Server::find($id);
if (!$server) { fwrite(STDERR, "no such server: $id\n"); exit(1); }

$repo = app(App\Repositories\Daemon\DaemonServerRepository::class)->setServer($server);
if ($action === 'status') {
    $d = $repo->getDetails();
    echo ($d['state'] ?? json_encode($d)), "\n";
    exit(0);
}
if (!in_array($action, ['start', 'stop', 'restart'], true)) {
    fwrite(STDERR, "refusing unknown action: $action\n"); exit(2);
}
$repo->power($action);
echo "sent '$action' to server $id ({$server->name})\n";
