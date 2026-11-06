<?php
namespace App\Jobs;

use const App\Config\VERSION;
use function App\Helpers\format;
use App\Models\{Document, Contact as Client};

trait Loggable {}

enum Status: string { case Draft = 'draft'; }

abstract class Job extends \Illuminate\Foundation\Bus\Dispatchable implements \Countable, Printable
{
    use Loggable, Helpers\Formatter;
}

interface Special extends Printable, \Stringable {}