program SortRandom;
const
   MAX_SIZE = 10;

var
   i   : integer;

function random_number(seed : longint): real;
const
   IM	= 139968;
   IA	= 3877;
   IC	= 29573;
begin
   seed := (seed * IA + IC) mod IM;
   random_number := seed * (1 / IM)
end;


begin
   for i := 0 to MAX_SIZE do
      random_number(i);
end.