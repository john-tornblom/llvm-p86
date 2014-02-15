Program WorkProgram;
Type
   DAY_T = (MON, TUE, WED, THU, FRI, SAT, SUN);

Function IsWorkday1(d: DAY_T) : Boolean;
Begin
   If (d = MON) or (d = TUE) or (d = WED) or (d = THU) or (d = FRI) Then
      IsWorkday1 := True
   Else
      IsWorkday1:= False;
End; { IsWorkday1 }


Function IsWorkday2(d : DAY_T) : Boolean;
Begin
   If (d = SAT) or (d = SUN) Then
      IsWorkday2 := False
   Else
      IsWorkday2 := True;
End; { IsWorkday2 }


Function IsWorkday3(d : DAY_T) : Boolean;
Begin
   IsWorkday3 := d in [MON, TUE, WED, THU, FRI];
End; { IsWorkday3 }



Function IsWorkday4(d : DAY_T) : Boolean;
Begin
   IsWorkday4 := not (d in [SAT, SUN]);
End; { IsWorkday4 }


Function IsWorkday5(d : DAY_T) : Boolean;
Begin
   IsWorkday5 := d <= FRI;
End; { IsWorkday5 }


Function IsWorkday6(d : DAY_T) : Boolean;
Begin
   IsWorkday6 := d < SUN;
End; { IsWorkday6 }

Begin
   If (ParamCount > 0) and (GetMutationCount > 0) Then
   Begin
      SetMutation(ord(ParamStr(1)));
      WriteLn('Executing mutant: ', GetMutationId);
   End;

   WriteLn('Mon ', IsWorkday1(MON));
   WriteLn('Tue ', IsWorkday1(TUE));
   WriteLn('Wed ', IsWorkday1(WED));
   WriteLn('Thu ', IsWorkday1(THU));
   WriteLn('Fri ', IsWorkday1(FRI));
   WriteLn('Sat ', IsWorkday1(SAT));
   WriteLn('Sun ', IsWorkday1(SUN));
End.
