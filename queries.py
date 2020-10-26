

first_page = """{ 
  repository(owner: "%s", name: "%s") {
    name
    %s(first:100){
      pageInfo {
        hasNextPage 
        hasPreviousPage 
      }
      edges{
        cursor
      }
      nodes{
        number 
        url
        createdAt 
        title 
        body 
        timelineItems(first:100){
          nodes{
            ... on CrossReferencedEvent{
              actor{
                login 
              }
              createdAt 
              id 
              isCrossRepository 
              referencedAt 
              resourcePath 
              source {
                ... on Issue{
                  number 
                  url
                  title
                }
                ... on PullRequest{
                  number 
                  url
                  title
                  id 
                }
              }
              target {
                ... on Issue{
                  number 
                  title
                }
                ... on PullRequest{
                  number 
                  title
                  id 
                }
              }
              url 
              willCloseTarget 
            }
          }
          pageInfo{
            hasNextPage
          }
          totalCount
        }
      }
      totalCount
    }
  }
}
"""

other_page = """{ 
  repository(owner: "%s", name: "%s") {
    name
    %s (first:100,after:"%s"){
      pageInfo {
        hasNextPage 
        hasPreviousPage 
      }
      edges{
        cursor
      }
      nodes{
        number 
        url
        createdAt 
        title 
        body 
        timelineItems(first:100){
          nodes{
            ... on CrossReferencedEvent{
              actor{
                login 
              }
              createdAt 
              id 
              isCrossRepository 
              referencedAt 
              resourcePath 
              source {
                ... on Issue{
                  number 
                  url
                  title
                }
              } 
              source {
                ... on PullRequest{
                  number 
                  url
                  title
                  id 
                }
              }
              target {
                ... on Issue{
                  number 
                  title
                }
                ... on PullRequest{
                  number 
                  title
                  id 
                }
              }
              url 
              willCloseTarget 
            }
          }
          pageInfo{
            hasNextPage
          }
          totalCount
        }
      }
      totalCount
    }
  }
}
"""

