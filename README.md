# SCaReM
The Summer Camp Resource Manager

This repository contains code for a web application that manages facility requests for a summer camp program.  The
application is written in python and uses django and mysql.

The django admin interface can be used to create the following:
  * *Resources* a.k.a. facilities are items that can be reserved.  This could be a particular building, a piece of A/V equipment,
  even a person.  Whatever the camps need to reserve.
  * *Tags* which can be attached to resources.  Tags are used to help narrow down the resource options when making a reservation.
  They can be things like "outdoor" or "has a stage" or whatever would be helpful.
  * *Camps* are organizations within the camping program that need to reserve facilities.
  
Reservations themselves are managed on the frontend interface.  Users can add, edit or delete reservations.  (Though reservations
cannot be made or edited less than a week out.)  Reservations can be viewed by camp, resource or date range.

This application was designed for use by [Shrine Mont Summer Camps](http://www.shrinemontcamps.net/).  That is currently the only
intended customer.  The code is written to be general purpose and could be reused by another camp program, but there are
things that would ideally move into a settings file to be customized by camps in this case.  (For example, the restriction
on editing reservations more than a week out may not be appropriate for every camp.)

If you would like to use this program for your camp, you are welcome to adopt the code according to the terms of
[the license](LICENSE.txt) and customize as needed.  PRs are welcome.  Or get in touch with me about making it more customizable.
