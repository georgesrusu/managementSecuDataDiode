<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>My administration</title>
  <!-- Le styles -->
  <link href="./css/bootstrap.css" rel="stylesheet">

  <style>
    body {
      padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
    }
  </style>
  <link href="./css/bootstrap-responsive.css" rel="stylesheet">
</head>


<body>
  <?php include("navbarAdmin.php"); $persons= null?>
  <h1>Welcome </h1>
  <div class="container">

    <h1>Search updates</h1> <!== 60px to make the container go all the way to the bottom of the topbar --!>

  <form class="form-search" action="search.php" method="post">
      <input type="text" name="personName" class="input-block-level" placeholder="Search..">
      <br><br>
      <button class="btn btn-primary" type="submit">Search</button>
    </form>

      <table class="table table-striped">
        <thead>
          <tr>
            <th> Package </th>
            <th> Version </th>
            <th> Size </th>
            <th> Action </th>
          </tr>
        </thead>
        <tbody>
            <tr>
              <td>John</td>
              <td>1</td>
              <td>12mo</td>
              <td>
                <a href="#">
                  <span class="icon-download-alt"></span>
                </a>
              </td>
            </tr>
            <tr>
              <td>Mary</td>
              <td>2.5</td>
              <td>5mo</td>
              <td>
                <a href="#">
                  <span class="icon-download-alt"></span>
                </a>
              </td>
            </tr>
            <tr>
              <td>July</td>
              <td>3.002</td>
              <td>0.7mp</td>
              <td>
                <a href="#">
                  <span class="icon-download-alt"></span>
                </a>
              </td>
            </tr>
          </tbody>
      </table>


  </div> <!-- /container -->

  <!-- Optional JavaScript -->
  <!-- jQuery first, then Popper.js, then Bootstrap JS -->
  <script src="./js/jquery.js"></script>
  <script src="./js/bootstrap.js"></script>
</body>
</html>
