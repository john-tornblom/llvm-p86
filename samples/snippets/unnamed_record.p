Program UnnamedRecordTest;

Var	 
   date	: Record
	     day   : Integer;
	     month : Integer;
	     year  : Integer;
	  End;	   

Procedure Assign(Var ref : Integer; value : Integer);
Begin
   ref := value;
End; { Assign }


Procedure Assert(value, expected : Integer);
Begin
   If value = expected Then
      Writeln('OK')
   Else
      Halt(1);
End; { Assert }

begin

   Assign(date.year, 1984);
   Assign(date.month, 1);
   Assign(date.day, 3);

   Assert(date.year, 1984);
   Assert(date.month, 1);
   Assert(date.day, 3);

   With date Do
   Begin
      Assign(year, 1984);
      Assign(month, 1);
      Assign(day, 3);

      Assert(year, 1984);
      Assert(month, 1);
      Assert(day, 3);
   End;

end.