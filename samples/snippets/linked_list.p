program PointerTest;

const
   OK = 'OK';

type
   P_LIST = ^T_LIST;
   T_LIST = record
	       num  : integer;
	       next : P_LIST;
	    end;    

var
   pList : ^T_LIST;
   p	 : ^T_LIST;
   i	 : integer;
begin
    new(p);
    dispose(p);

   pList := nil;
   for i := 1 to 5 do begin
      new(p);
      p^.num := i;
      p^.next := pList;
      pList := p;
   end;

   i := 0;
   repeat
      p := pList;
      i := i + p^.num;
      pList := p^.next;
      dispose(p);
      
      if p = nil then
	 writeln('OK')
      else
	 halt(1);
   until pList = nil;

   if i = 15 then
      writeln('OK')
   else
      halt(1);

end.
