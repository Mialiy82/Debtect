<?php

namespace App\Models\Document;

use App\Abstracts\Model;
use App\Traits\{Contacts, Currencies};
use Illuminate\Database\Eloquent\Builder as QueryBuilder;
use function App\Helpers\format;

interface Printable {}

class Document extends Model implements Printable
{
    use Contacts, Currencies;
}
