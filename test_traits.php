<?php

class X {
    use A, B {
        A::hello insteadof B;
    }
}